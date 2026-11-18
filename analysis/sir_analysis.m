% Analytical SIR model - paper Sec. III-C, eq. (4), Table III  (MATLAB / Octave)
% k*cot(0.5*alpha*theta_t) = tan((1-alpha)*0.5*theta_t)
clear; clc;
c = 299.792458;              % mm*GHz
k = 0.45644; alpha = 0.7306; % from the paper
eeff1 = 2.03; eeff2 = 2.40;  % thin / wide CPS sections (back-calculated, see README)

g  = @(t) k./tan(0.5*alpha*t) - tan((1-alpha)*0.5*t);
tt = fzero(g, [1e-4, 1.5*pi]);
th1 = 0.5*(1-alpha)*tt;  th2 = 0.5*alpha*tt;
fprintf('theta_t = %.2f deg (UIR: 180 deg)\n', rad2deg(tt));
fprintf('theta1 = %.2f deg, theta2 = %.2f deg\n', rad2deg(th1), rad2deg(th2));

f = [1.5 1.8 2.2 2.6];
l1 = 2*th1*c./(2*pi*f*sqrt(eeff1));
l2 =   th2*c./(2*pi*f*sqrt(eeff2));
l1_paper = [15.08 12.571 10.29 8.7];  l2_paper = [18.79 15.66 12.8 10.84];
disp(table(f', l1', l1_paper', l2', l2_paper', 'VariableNames', ...
     {'f_GHz','l1_ours','l1_paper','l2_ours','l2_paper'}));

ks = linspace(0.15,1.5,200); tts = zeros(size(ks));
for i = 1:numel(ks)
    gi = @(t) ks(i)./tan(0.5*alpha*t) - tan((1-alpha)*0.5*t);
    tts(i) = rad2deg(fzero(gi, [1e-4, 1.5*pi]));
end
figure; plot(ks, tts, 'LineWidth', 2); hold on; yline(180,'--','UIR (k=1)');
plot(k, rad2deg(tt), 'ro'); grid on;
xlabel('k = Z_2/Z_1'); ylabel('\theta_t (deg)'); title('SIR length vs impedance ratio');
