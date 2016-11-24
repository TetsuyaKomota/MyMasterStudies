% -------------------------------------------------------------------------
%
% File : Unscented KalmanFilterLocalization.m
%
% Discription : Mobible robot localization sample code with
%               Unscented Kalman Filter (UKF)
%
% Environment : Matlab
%
% Author : Atsushi Sakai
%
% Copyright (c): 2014 Atsushi Sakai
%
% License : Modified BSD Software License Agreement
% -------------------------------------------------------------------------
 
function [] = UnscentedKalmanFilterLocalization()
 
close all;
clear all;
 
disp('Unscented Kalman Filter (UKF) sample program start!!')
 
% G-flag (for debug)
global gFlag
gFlag = true;
 % -----------------------------------------
% UKF Parameter
alpha=0.001;
beta =2;
kappa=0;

% Covariance Matrix
PEst = eye(4).*1;
 % -----------------------------------------

time = 0;
endtime = 0.5; % [sec]
if gFlag
    endtime = endtime / 10;
end
global dt;
dt = 0.01; % [sec]
 
nSteps = ceil((endtime - time)/dt);
 
% State Vector [x y yaw v]'
xEst=[0 pi/4 0 0]';
 
% True State
xTrue=xEst;
 


% Dead Reckoning
xd=xTrue;

% Observation vector [x y yaw v]'
z=[0]';

result.time=[];
result.xTrue=[xTrue'];
result.xd=[xd'];
result.xEst=[xEst'];
result.z=[z];
result.PEst=[diag(PEst)'];
result.u=[];

% Covariance Matrix for predict
Q=diag([0.0001 0.0001 0.0001 0.0001]);
 
% Covariance Matrix for observation
R=diag([0.0001]);

% Simulation parameter
global Qsigma
Qsigma=diag([0.0001 0.0001]);
 
global Rsigma
Rsigma=diag([0.0001]);

global l1
l1=0.5;
global l2
l2=0.25;
global a1
a1=1.0;
global a2
a2=0.5;
global m1
m1=10.0;
global m2
m2=5.0;
global I1
I1=5.0;
global I2
I2=0.5;
global d1
d1=0.0;
global d2
d2=0.0;
global g
g=9.8;

n=length(xEst);%size of state vector
lamda=alpha^2*(n+kappa)-n;

%calculate weights
wm=[lamda/(lamda+n)];
wc=[(lamda/(lamda+n))+(1-alpha^2+beta)];
% wc=[(lamda/(lamda+n))];
for i=1:2*n
    wm=[wm 1/(2*(n+lamda))];
    wc=[wc 1/(2*(n+lamda))];
end
wmall = sum(wm);
wcall = sum(wc);
gamma=sqrt(n+lamda);

%movcount=0;
tic;
% Main loop
for i=1 : nSteps
    time = time + dt;
    % Input
    u=doControl(time);
    % Observation
    [z,xTrue,xd,u]=Observation(xTrue, xd, u);
    
    % ------ Unscented Kalman Filter --------
    % Predict 
    sigma=GenerateSigmaPoints(xEst,PEst,gamma);
    sigma=PredictMotion(sigma,u);
    xPred=(wm*sigma')';
    PPred=CalcSimgaPointsCovariance(xPred,sigma,wc,Q);
    
    % Update
    y = z - h(xPred);
    sigma=GenerateSigmaPoints(xPred,PPred,gamma);
    zSigma=PredictObservationZ(sigma);
    zb=(wm*zSigma')';
    St=CalcSimgaPointsCovariance(zb,zSigma,wc,R);
    Pxz=CalcPxz(sigma,xPred,zSigma,zb,wc);
    K=Pxz*inv(St);
    xEst = xPred + K*y;
    PEst=PPred-K*St*K';
    
    % Simulation Result
    result.time=[result.time; time];
    result.xTrue=[result.xTrue; xTrue'];
    result.xd=[result.xd; xd'];
    result.xEst=[result.xEst;xEst'];
    result.z=[result.z; z'];
    result.PEst=[result.PEst; diag(PEst)'];
    result.u=[result.u; u'];    
    
end
toc

DrawGraph(result, nSteps);

function sigma=PredictMotion(sigma,u)
% Sigma Points predition with motion model
for i=1:length(sigma(1,:))
    sigma(:,i)=f(sigma(:,i),u);
end

function zSigma=PredictObservationZ(sigma)
% Sigma Points predition with observation model
for i=1:length(sigma(1,:))
    zSigma(:,i)=h(sigma(:,i));
end

function P=CalcSimgaPointsCovariance(xPred,sigma,wc,N)
nSigma=length(sigma(1,:));
d=sigma-repmat(xPred,1,nSigma);
P=N;
for i=1:nSigma
    P=P+wc(i)*d(:,i)*d(:,i)';
end

function P=CalcPxz(sigma,xPred,zSigma,zb,wc)
nSigma=length(sigma(1,:));
dx=sigma-repmat(xPred,1,nSigma);
dz=zSigma-repmat(zb,1,nSigma);
P = [0 0 0 0]';
for i=1:nSigma
    P=P+wc(i)*dx(:,i)*dz(:,i)';
end

function sigma=GenerateSigmaPoints(xEst,PEst,gamma)
sigma=xEst;
Psqrt=sqrtm(PEst);
n=length(xEst);
%Positive direction
for ip=1:n
    sigma=[sigma xEst+gamma*Psqrt(:,ip)];
end
%Negative direction
for in=1:n
    sigma=[sigma xEst-gamma*Psqrt(:,in)];
end

function xd = f(x, u)
% Motion Model
 
global dt;
 
global m1;
global m2;
global l1;
global l2;
global I1;
global I2;
global a1;

fai1 = m1*l1*l1 + m2*a1*a1 + I1;
fai2 = m2*l2*l2 + I2;
fai3 = m2*a1*l2;

D = [fai1+fai2+2*fai3*cos(x(2)) fai2+fai3*cos(x(2)) ; fai2+fai3*cos(x(2)) fai2];
X = [x(4) x(3)+x(4) ; -x(3) 0];
qd = [x(3) x(4)]';

global gFlag;
if gFlag
    ttd = inv(D) * (X*qd.*(fai3*sin(x(2))) - PowerofGravity(x(1), x(2)));
else
    ttd = inv(D) * (X*qd.*(fai3*sin(x(2))));
end
    
xd= [x(3) x(4) ttd']';

function G = PowerofGravity(x1, x2)
global m1;
global m2;
global l1;
global l2;
global a1;
global a2;
global g;
g1 = m1*l1*cos(x1) + m2*(a1*cos(x1) + l2*cos(x1+x2));
g2 = m2*l2*cos(x1+x2);
G = [g1 g2]'.*g;

function z = h(x)
%Observation Model
global l1;
global l2;
z = l1*cos(x(1)) + l2*cos(x(1)+x(2));

function u = doControl(time)
u =[0 0]'; 
 
%Calc Observation from noise prameter
function [z, x, xd, u] = Observation(x, xd, u)
global Qsigma;
global Rsigma;
 
x=f(x, u);% Ground Truth
u=u+Qsigma*randn(2,1);%add Process Noise
xd=f(xd, u);% Dead Reckoning
z=h(x+Rsigma*randn(1,1));%Simulate Observation

function []=DrawGraph(result, numofStep)

xEst = result.xEst;
xTrue = result.xTrue;

figure(1);

subplot(2, 2, 1);
plot(0:length(xEst(:, 1) )-1, xEst(:, 1), 'LineWidth', 3);hold on;
plot(0:length(xTrue(:, 1))-1, xTrue(:,1), 'LineWidth', 3);hold on;
xlabel('time step');
ylabel('theta1');
legend('Estimated', 'truth');
grid on;
subplot(2, 2, 2);
plot(0:length(xEst(:, 1) )-1, xEst(:, 2), 'LineWidth', 3);hold on;
plot(0:length(xTrue(:, 1))-1, xTrue(:,2), 'LineWidth', 3);hold on;
xlabel('time step');
ylabel('theta2');
legend('Estimated', 'truth');
grid on;
subplot(2, 2, 3);
plot(0:length(xEst(:, 1) )-1, xEst(:, 3), 'LineWidth', 3);hold on;
plot(0:length(xTrue(:, 1))-1, xTrue(:,3), 'LineWidth', 3);hold on;
xlabel('time step');
ylabel('dtheta1');
legend('Estimated', 'truth');
grid on;
subplot(2, 2, 4);
plot(0:length(xEst(:, 1) )-1, xEst(:, 4), 'LineWidth', 3);hold on;
plot(0:length(xTrue(:, 1))-1, xTrue(:,4), 'LineWidth', 3);hold on;
xlabel('time step');
ylabel('dtheta2');
legend('Estimated', 'truth');
grid on;