function generate_gpr_hil_vectors(outdir)
if nargin<1, outdir='build/hil_vectors'; end
if ~exist(outdir,'dir'), mkdir(outdir); end
rng(11);
c=299792458;
nT=256; nFFT=2048; nPos=64;
f=linspace(500e6,3e9,nT).';
x=linspace(0,6,nPos);
epsr=4.0; v=c/sqrt(epsr);
targets=[1.5 0.25 1.0; 3.0 0.55 0.65; 4.8 0.8 0.8]; % x, depth, amplitude
S=zeros(nT,nPos);
for p=1:nPos
    for t=1:size(targets,1)
        R=sqrt(targets(t,2)^2+(x(p)-targets(t,1))^2);
        S(:,p)=S(:,p)+targets(t,3)./max(R,0.05).^2 .* exp(-1j*4*pi*f*R/v);
    end
end
% Add repeatable direct coupling and noise.
coupling=0.25*exp(1j*(0.6+2*pi*(f-f(1))/(f(end)-f(1))*0.03));
S=S+coupling;
S=S+0.003*(randn(size(S))+1j*randn(size(S)));

w=kaiser(nT,6);
cal=ones(nT,1);
coef=w.*cal;
range=zeros(nFFT,nPos);
for p=1:nPos
    z=zeros(nFFT,1); z(1:nT)=S(:,p).*coef;
    range(:,p)=ifft(z);
end
bg=median(range,2);
clean=range-bg;
power=abs(clean).^2;
save(fullfile(outdir,'gpr_hil_reference.mat'),'S','coef','range','clean','power','f','x','targets','epsr');

% Fixed-point stream vectors, I[15:0],Q[31:16]
scale=12000/max(abs(S(:)));
iq=int16(max(-32768,min(32767,round([real(S(:))*scale imag(S(:))*scale]))));
fid=fopen(fullfile(outdir,'rx_iq_s16le.bin'),'w'); fwrite(fid,iq.','int16'); fclose(fid);

cq=int16(max(-32768,min(32767,round([real(coef)*32767 imag(coef)*32767]))));
fid=fopen(fullfile(outdir,'cal_window_q15.bin'),'w'); fwrite(fid,cq.','int16'); fclose(fid);

manifest=struct('n_tones',nT,'n_ifft',nFFT,'n_positions',nPos,'eps_r',epsr, ...
    'format','complex int16 little-endian: I then Q; coefficient Q1.15');
fid=fopen(fullfile(outdir,'manifest.json'),'w');
fprintf(fid,'%s',jsonencode(manifest,PrettyPrint=true)); fclose(fid);
fprintf('Generated GPR HIL vectors in %s\n',outdir);
end
