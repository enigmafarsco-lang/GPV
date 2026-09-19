function plan = generate_gpr_hybrid_v3_plan(outdir, f_start, f_stop, n_tones, tones_per_subband, fabric_hz)
if nargin < 1 || isempty(outdir), outdir='build/hil_vectors'; end
if nargin < 2, f_start=500e6; end
if nargin < 3, f_stop=3e9; end
if nargin < 4, n_tones=256; end
if nargin < 5, tones_per_subband=12; end
if nargin < 6, fabric_hz=245.76e6; end
if ~exist(outdir,'dir'), mkdir(outdir); end

df=(f_stop-f_start)/(n_tones-1);
res0=-0.5*(tones_per_subband-1)*df;
tone=(0:n_tones-1).';
sb=floor(tone/tones_per_subband);
local=mod(tone,tones_per_subband);
residual=res0+local*df;
rf=f_start+tone*df;
lo=rf-residual;
step=mod(round(residual/fabric_hz*2^48),2^48);

plan=table(tone,sb,local,rf,lo,residual,step);
writetable(plan,fullfile(outdir,'hybrid_v3_sweep_plan.csv'));
save(fullfile(outdir,'hybrid_v3_sweep_plan.mat'),'plan','df','res0','fabric_hz');
fprintf('Hybrid V3 plan: %d tones, %d subbands -> %s\n',n_tones,max(sb)+1,outdir);
end
