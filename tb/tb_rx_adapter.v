// ---------------------------------------------------------------------------
// tb_rx_adapter.v - self-checking test for gpr_rx_adapter.
//
// Synthesises the exact waveform the TX DDS would transmit after RFDC
// sub-band mixing: each tone arrives at the residual frequency
// fw_rom[seq] - sb_center_fw, phase-coherent from 0 (the DDS restarts phase
// per tone).  The adapter must derotate, integrate over the dwell, normalise
// by the dwell and emit ONE tagged beat per tone with (A, 0) within a few
// LSB.  Two phases exercise sb_center_fw = 0 and a non-zero centre.
// Also checks: 4-samples-per-beat gearbox ordering, tuser tone/pos tags,
// tlast per sweep, pos_done per position, input gaps and output backpressure.
// ---------------------------------------------------------------------------
`timescale 1ns / 1ps
module tb_rx_adapter;
    localparam NT = 16, SPC = 4, DWELL = 8, NAVGM1 = 1;
    localparam NBEAT_FRAME = 2*NT*(NAVGM1+1);          // 64 output beats
    localparam NSAMP_FRAME = NBEAT_FRAME*DWELL;        // 512 samples
    localparam signed [15:0] AMP = 16'd16384;

    reg clk = 0, rst = 1;
    reg [31:0] dwell_cyc = DWELL;
    reg [7:0]  n_avg_m1  = NAVGM1;
    reg [47:0] sb_center = 48'd0;

    reg              s_tvalid = 0;
    wire             s_tready;
    reg [SPC*32-1:0] s_tdata = 0;

    wire        m_tvalid, m_tlast, pos_done;
    wire [31:0] m_tdata;
    wire [7:0]  m_tuser_tone, m_tuser_pos;
    reg         m_tready = 1;

    gpr_rx_adapter #(
        .N_TONES(NT), .SPC(SPC),
        .FW_FILE("fw_seq_t.hex"), .TIDX_FILE("tidx_seq_t.hex"),
        .SINE_FILE("sine_rom.hex")
    ) dut (
        .clk(clk), .rst(rst),
        .dwell_cyc(dwell_cyc), .n_avg_m1(n_avg_m1), .sb_center_fw(sb_center),
        .s_tvalid(s_tvalid), .s_tready(s_tready), .s_tdata(s_tdata),
        .s_tlast(1'b0),
        .m_tvalid(m_tvalid), .m_tready(m_tready), .m_tdata(m_tdata),
        .m_tlast(m_tlast), .m_tuser_tone(m_tuser_tone),
        .m_tuser_pos(m_tuser_pos), .pos_done(pos_done), .tone_seq_idx());

    always #2 clk = ~clk;

    // ---- ROMs mirrored from the DUT ---------------------------------------
    reg [47:0] fw_rom [0:NT-1];
    reg [7:0]  tidx_rom [0:NT-1];
    reg [15:0] sine_rom [0:4095];
    initial begin
        $readmemh("fw_seq_t.hex", fw_rom);
        $readmemh("tidx_seq_t.hex", tidx_rom);
        $readmemh("sine_rom.hex", sine_rom);
    end

    // ---- waveform generation (mirrors gpr_dds_txc exactly) -----------------
    reg signed [15:0] samp_i [0:NSAMP_FRAME-1];
    reg signed [15:0] samp_q [0:NSAMP_FRAME-1];

    task gen_frame_samples;
        integer b, k, n;
        reg [47:0] ph, fw;
        reg [1:0] quad;
        reg [11:0] sa;
        reg signed [15:0] s0, s1, sv, cv;
        reg signed [32:0] pi_, pq_;
        begin
            n = 0;
            for (b = 0; b < NBEAT_FRAME; b = b + 1) begin
                fw = fw_rom[b % NT] - sb_center;      // mod 2^48
                ph = 48'd0;                            // coherent tone start
                for (k = 0; k < DWELL; k = k + 1) begin
                    quad = ph[47:46];
                    sa   = ph[45:34];
                    s0   = $signed(sine_rom[sa]);
                    s1   = $signed(sine_rom[12'd4095 - sa]);
                    case (quad)
                        2'd0:    begin sv =  s0; cv =  s1; end
                        2'd1:    begin sv =  s1; cv = -s0; end
                        2'd2:    begin sv = -s0; cv = -s1; end
                        default: begin sv = -s1; cv =  s0; end
                    endcase
                    pi_ = AMP * cv;
                    pq_ = AMP * sv;
                    samp_i[n] = sat16tb((pi_ + 33'sd16384) >>> 15);
                    samp_q[n] = sat16tb((pq_ + 33'sd16384) >>> 15);
                    ph = ph + fw;
                    n = n + 1;
                end
            end
        end
    endtask

    function signed [15:0] sat16tb(input signed [32:0] v);
        begin
            if      (v >  33'sd32767) sat16tb =  16'sd32767;
            else if (v < -33'sd32768) sat16tb = -16'sd32768;
            else                      sat16tb = v[15:0];
        end
    endfunction

    // ---- stimulus ----------------------------------------------------------
    integer errors = 0;
    integer out_cnt = 0, pd_cnt = 0, phase_no = 0;
    integer gap_lfsr = 17;
    reg signed [15:0] vi, vq;
    integer seq_e, pos_e, sweep_e;

    always @(posedge clk) begin
        if (!rst && pos_done) pd_cnt = pd_cnt + 1;
        if (!rst && m_tvalid && m_tready) begin
            seq_e   = out_cnt % NT;
            sweep_e = (out_cnt / NT) % (NAVGM1+1);
            pos_e   = phase_no*2 + ((out_cnt % NBEAT_FRAME) / (NT*(NAVGM1+1)));
            vi = $signed(m_tdata[31:16]);
            vq = $signed(m_tdata[15:0]);
            if (m_tuser_tone !== tidx_rom[seq_e]) begin
                $display("beat %0d: tone tag %0d want %0d", out_cnt,
                         m_tuser_tone, tidx_rom[seq_e]);
                errors = errors + 1;
            end
            if (m_tuser_pos !== pos_e[7:0]) begin
                $display("beat %0d: pos tag %0d want %0d", out_cnt,
                         m_tuser_pos, pos_e);
                errors = errors + 1;
            end
            if (m_tlast !== (seq_e == NT-1)) begin
                $display("beat %0d: tlast %b want %b", out_cnt, m_tlast,
                         (seq_e == NT-1));
                errors = errors + 1;
            end
            if (vi < AMP-48 || vi > AMP+48 || vq < -48 || vq > 48) begin
                $display("beat %0d: value (%0d,%0d) want (~%0d,~0)",
                         out_cnt, vi, vq, AMP);
                errors = errors + 1;
            end
            out_cnt = out_cnt + 1;
        end
    end

    task drive_frame;
        integer j, k, g;
        begin
            for (j = 0; j < NSAMP_FRAME/SPC; j = j + 1) begin
                // pseudo-random idle gaps
                gap_lfsr = gap_lfsr*5 + 7;
                g = (gap_lfsr >> 3) % 4;
                s_tvalid <= 0;
                repeat (g) @(posedge clk);
                for (k = 0; k < SPC; k = k + 1)
                    s_tdata[32*k +: 32] <= {samp_i[j*SPC+k], samp_q[j*SPC+k]};
                s_tvalid <= 1;
                @(posedge clk);
                while (!s_tready) @(posedge clk);
            end
            @(posedge clk);
            s_tvalid <= 0;
        end
    endtask

    initial begin
        repeat (4) @(posedge clk);
        rst = 0;
        repeat (2) @(posedge clk);

        // ---- phase 1: sb_center = 0, with an output-stall window ----------
        phase_no = 0; sb_center = 48'd0;
        gen_frame_samples;
        fork
            drive_frame;
            begin                      // stall the consumer mid-frame
                repeat (300) @(posedge clk);
                m_tready <= 0;
                repeat (100) @(posedge clk);
                m_tready <= 1;
            end
        join
        wait (out_cnt == NBEAT_FRAME);
        repeat (50) @(posedge clk);
        if (pd_cnt !== 2) begin
            $display("phase1: pos_done %0d want 2", pd_cnt);
            errors = errors + 1;
        end

        // ---- phase 2: non-zero sub-band centre -----------------------------
        phase_no = 1; sb_center = 48'h123456789ABC;
        pd_cnt = 0;
        gen_frame_samples;
        drive_frame;
        wait (out_cnt == 2*NBEAT_FRAME);
        repeat (50) @(posedge clk);
        if (pd_cnt !== 2) begin
            $display("phase2: pos_done %0d want 2", pd_cnt);
            errors = errors + 1;
        end

        if (errors == 0) $display("TB_RX_ADAPTER PASS (%0d beats)", out_cnt);
        else             $display("TB_RX_ADAPTER FAIL (%0d errors)", errors);
        $finish;
    end

    initial begin
        #20000000;
        $display("TB_RX_ADAPTER TIMEOUT (out_cnt=%0d)", out_cnt);
        $finish;
    end
endmodule
