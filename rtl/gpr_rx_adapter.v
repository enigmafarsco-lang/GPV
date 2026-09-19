// ---------------------------------------------------------------------------
// gpr_rx_adapter.v - RFDC-facing receive front-end for the GPR chain.
//
// Real RF-ADC AXI4-Stream output differs from the internal loopback stream in
// three ways this adapter absorbs (see GPV_COMPARISON_NOTES of the hybrid-v3
// review - these were its valid architectural points):
//
//   1. WIDTH/PACKING: the RFDC delivers SPC (default 4) {I,Q} Q15 samples per
//      128-bit beat.  A ping-pong gearbox unpacks to one sample per fabric
//      clock with full throughput and lossless backpressure.
//   2. NO METADATA: the RFDC carries no tone/position TUSER.  A beat
//      scheduler derives tone index, sweep and position purely from
//      dwell_cyc / N_TONES / n_avg_m1 counting, exactly mirroring the TX
//      sequencer in gpr_dds_txc.
//   3. RESIDUAL CARRIER: the RFDC fine mixer tunes to the SUB-BAND centre, so
//      each captured tone sits at a residual IF f_res = f_tone - f_sb.  The
//      adapter derotates every sample with an NCO (fw_rom[tone] -
//      sb_center_fw, same 48-bit phase / quarter-wave sine ROM scheme as the
//      DDS, phase restarted at 0 on every tone = coherent with the TX tone
//      start), BEFORE dwell integration, so the coherent sum does not cancel.
//
// Dwell integration (sum of dwell_cyc derotated samples, 40-bit guard
// accumulators) and exact dwell normalisation (round-to-nearest divide by
// dwell_cyc via gpr_div) happen HERE - one output beat per tone - and are
// therefore separate from the n_avg cross-sweep averaging in gpr_avg, which
// keeps its documented "one sample per tone per sweep" semantics.
//
// Output stream is a drop-in replacement for the loopback DDS stream:
// 32-bit {I,Q} Q15, tuser_tone = TRUE tone index (tidx ROM), tuser_pos,
// tlast on the last tone of a sweep, pos_done pulse per completed position.
//
// Constraints: dwell_cyc in [1, 65535]; sustained input rate <= 1 sample per
// fabric clock (normalisation pauses ~70 cycles per tone, absorbed by the
// ping-pong buffers and RFDC FIFOs).
// ---------------------------------------------------------------------------
`timescale 1ns / 1ps
module gpr_rx_adapter #(
    parameter N_TONES   = 256,
    parameter SPC       = 4,                 // samples per input beat
    parameter FW_FILE   = "fw_seq_a.hex",
    parameter TIDX_FILE = "tidx_seq_a.hex",
    parameter SINE_FILE = "sine_rom.hex"
) (
    input  wire        clk,
    input  wire        rst,
    // configuration (AXI-Lite registers in gpr_top)
    input  wire [31:0] dwell_cyc,            // samples per tone (>=1)
    input  wire [7:0]  n_avg_m1,             // sweeps per position minus 1
    input  wire [47:0] sb_center_fw,         // RFDC mixer centre, Q0.46 turns
    // RFDC AXI4-Stream slave (no TUSER; tlast ignored)
    input  wire             s_tvalid,
    output wire             s_tready,
    input  wire [SPC*32-1:0] s_tdata,
    input  wire             s_tlast,
    // tagged tone stream to gpr_adc_if
    output reg         m_tvalid,
    input  wire        m_tready,
    output reg  [31:0] m_tdata,
    output reg         m_tlast,
    output reg  [7:0]  m_tuser_tone,
    output reg  [7:0]  m_tuser_pos,
    output reg         pos_done,
    output reg  [7:0]  tone_seq_idx
);
    localparam [1:0] SA_START = 2'd0, SA_RUN = 2'd1,
                     SA_NORM  = 2'd2, SA_EMIT = 2'd3;

    // ---- ROMs (shared content with the TX DDS: same tone plan) -------------
    reg [47:0] fw_rom   [0:N_TONES-1];
    reg [7:0]  tidx_rom [0:N_TONES-1];
    reg [15:0] sine_rom [0:4095];
    initial begin
        $readmemh(FW_FILE,   fw_rom);
        $readmemh(TIDX_FILE, tidx_rom);
        $readmemh(SINE_FILE, sine_rom);
    end

    // ---- ping-pong input gearbox -------------------------------------------
    reg [31:0] bufA [0:SPC-1];
    reg [31:0] bufB [0:SPC-1];
    reg        a_full, b_full;      // buffer holds an unprocessed beat
    reg        fill_a;              // next accepted beat lands in A
    reg        proc_a;              // samples are taken from A
    reg [7:0]  proc_idx;

    wire       proc_has = proc_a ? a_full : b_full;
    wire [31:0] psamp   = proc_a ? bufA[proc_idx[7:0]] : bufB[proc_idx[7:0]];
    assign s_tready = fill_a ? !a_full : !b_full;
    wire   s_fire   = s_tvalid && s_tready;

    // ---- scheduler / NCO state ---------------------------------------------
    reg [1:0]  st;
    reg [7:0]  tone_i, avg_i, pos_i;
    reg [31:0] sample_cnt;
    reg [47:0] phase;
    // live residual word: recomputed from the CURRENT sb_center_fw so a PS
    // sub-band retune at a tone boundary takes effect on the very next tone
    // (no stale pre-armed value).
    wire [47:0] fw_res = fw_rom[tone_i] - sb_center_fw;
    reg signed [39:0] acc_i, acc_q;
    reg        norm_q;              // 0 = normalising I, 1 = Q
    reg        dstart;
    reg signed [15:0] qi, qq;

    // quarter-wave sine evaluation (identical scheme to gpr_dds_txc)
    wire [1:0]  quad  = phase[47:46];
    wire [11:0] saddr = phase[45:34];
    wire signed [15:0] s0 = $signed(sine_rom[saddr]);
    wire signed [15:0] s1 = $signed(sine_rom[12'd4095 - saddr]);
    reg  signed [15:0] sin_v, cos_v;
    always @(*) begin
        case (quad)
            2'd0:    begin sin_v =  s0; cos_v =  s1; end
            2'd1:    begin sin_v =  s1; cos_v = -s0; end
            2'd2:    begin sin_v = -s0; cos_v = -s1; end
            default: begin sin_v = -s1; cos_v =  s0; end
        endcase
    end

    // derotated sample: x * (cos - j sin), Q15 x Q15 -> Q15 (rounded), the
    // 18-bit results accumulate without further rounding
    wire signed [15:0] xi = $signed(psamp[31:16]);
    wire signed [15:0] xq = $signed(psamp[15:0]);
    wire signed [32:0] mix_i = (xi * cos_v + xq * sin_v + 33'sd16384) >>> 15;
    wire signed [32:0] mix_q = (xq * cos_v - xi * sin_v + 33'sd16384) >>> 15;

    wire        dwell_end = (sample_cnt + 32'd1 >= dwell_cyc);

    // ---- normalisation divide (magnitude / dwell, round to nearest) --------
    wire signed [39:0] acc_sel = norm_q ? acc_q : acc_i;
    wire [39:0] mag40 = acc_sel[39] ? (~acc_sel + 40'd1) : acc_sel[39:0];
    wire [15:0] den16 = dwell_cyc[15:0];
    wire [31:0] mag32 = |mag40[39:31] ? 32'h7FFF_FFFF : {1'b0, mag40[30:0]};
    wire [31:0] num32 = mag32[31] ? mag32 : (mag32 + {16'd0, den16[15:1]});
    wire [31:0] dquo;
    wire        dbusy, ddone;
    gpr_div u_div (
        .clk(clk), .rst(rst), .start(dstart), .num(num32), .den(den16),
        .quo(dquo), .rem(), .busy(dbusy), .done(ddone));

    function signed [15:0] sat16(input signed [32:0] v);
        begin
            if      (v >  33'sd32767) sat16 =  16'sd32767;
            else if (v < -33'sd32768) sat16 = -16'sd32768;
            else                      sat16 = v[15:0];
        end
    endfunction

    integer q;
    always @(posedge clk) begin
        if (rst) begin
            a_full <= 0; b_full <= 0; fill_a <= 1; proc_a <= 1; proc_idx <= 0;
            st <= SA_START; tone_i <= 0; avg_i <= 0; pos_i <= 0;
            sample_cnt <= 0; phase <= 0;
            acc_i <= 0; acc_q <= 0; norm_q <= 0; dstart <= 0; qi <= 0; qq <= 0;
            m_tvalid <= 0; m_tdata <= 0; m_tlast <= 0;
            m_tuser_tone <= 0; m_tuser_pos <= 0;
            pos_done <= 0; tone_seq_idx <= 0;
        end else begin
            pos_done <= 1'b0;
            dstart   <= 1'b0;

            // ---- input side: fill the empty buffer ----
            if (s_fire) begin
                if (fill_a) begin
                    for (q = 0; q < SPC; q = q + 1)
                        bufA[q] <= s_tdata[32*q +: 32];
                    a_full <= 1'b1;
                end else begin
                    for (q = 0; q < SPC; q = q + 1)
                        bufB[q] <= s_tdata[32*q +: 32];
                    b_full <= 1'b1;
                end
                fill_a <= !fill_a;
            end

            case (st)
            // ----------------------------------------------------------
            SA_START: begin
                // coherent start: phase = 0 (fw_res is combinational)
                phase  <= 48'd0;
                st     <= SA_RUN;
            end
            // ----------------------------------------------------------
            SA_RUN: begin
                if (proc_has) begin
                    // derotate + integrate one sample
                    acc_i  <= acc_i + mix_i;
                    acc_q  <= acc_q + mix_q;
                    phase  <= phase + fw_res;
                    // consume the sample from the process buffer
                    if (proc_idx == SPC-1) begin
                        proc_idx <= 0;
                        proc_a   <= !proc_a;
                        if (proc_a) a_full <= 1'b0;
                        else        b_full <= 1'b0;
                    end else
                        proc_idx <= proc_idx + 1;

                    if (dwell_end) begin
                        // tone complete: normalise I then Q
                        sample_cnt <= 0;
                        norm_q     <= 1'b0;
                        dstart     <= 1'b1;
                        st         <= SA_NORM;
                    end else
                        sample_cnt <= sample_cnt + 1;
                end
            end
            // ----------------------------------------------------------
            SA_NORM: begin
                if (ddone) begin
                    if (!norm_q) begin
                        qi     <= sat16({1'b0, dquo});      // re-sign below
                        if (acc_i[39]) qi <= -sat16({1'b0, dquo});
                        norm_q <= 1'b1;
                        dstart <= 1'b1;
                    end else begin
                        qq     <= sat16({1'b0, dquo});
                        if (acc_q[39]) qq <= -sat16({1'b0, dquo});
                        st     <= SA_EMIT;
                    end
                end
            end
            // ----------------------------------------------------------
            SA_EMIT: begin
                m_tvalid     <= 1'b1;
                m_tdata      <= {qi, qq};
                m_tuser_tone <= tidx_rom[tone_i];
                m_tuser_pos  <= pos_i;
                m_tlast      <= (tone_i == N_TONES-1);
                tone_seq_idx <= tone_i;
                if (m_tvalid && m_tready) begin
                    m_tvalid <= 1'b0;
                    // advance the schedule exactly like the TX DDS
                    if (tone_i == N_TONES-1) begin
                        tone_i <= 8'd0;
                        if (avg_i == n_avg_m1) begin
                            avg_i    <= 8'd0;
                            pos_i    <= pos_i + 8'd1;
                            pos_done <= 1'b1;
                        end else
                            avg_i <= avg_i + 8'd1;
                    end else
                        tone_i <= tone_i + 8'd1;
                    // next tone: coherent NCO restart, clear integrators
                    // (fw_res follows tone_i combinationally)
                    acc_i  <= 40'sd0;
                    acc_q  <= 40'sd0;
                    phase  <= 48'd0;
                    st <= SA_RUN;
                end
            end
            default: st <= SA_START;
            endcase
        end
    end
endmodule
