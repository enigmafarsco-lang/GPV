function R=run_gpr_reference(matfile)
if nargin<1, matfile='build/hil_vectors/gpr_hil_reference.mat'; end
D=load(matfile);
R=D;
R.range_db=20*log10(abs(D.range)/max(abs(D.range(:)))+1e-12);
R.clean_db=20*log10(abs(D.clean)/max(abs(D.clean(:)))+1e-12);
figure('Name','GPR HIL reference');
subplot(1,2,1); imagesc(D.x,1:size(D.range,1),R.range_db); axis xy; title('Range profile stack'); xlabel('x (m)');
subplot(1,2,2); imagesc(D.x,1:size(D.clean,1),R.clean_db); axis xy; title('Background removed'); xlabel('x (m)');
end
