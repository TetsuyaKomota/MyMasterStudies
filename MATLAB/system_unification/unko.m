x1 = ones(1, 10);
x2 = [1:10].*2;
x3 = x2.^2;
x4 = x1./x2;

figure(1);

subplot(2, 2, 1), plot(x1');
subplot(2, 2, 2), plot(x2');
subplot(2, 2, 3), plot(x3');
subplot(2, 2, 4), plot(x4');

grid on;