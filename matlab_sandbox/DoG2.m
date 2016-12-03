function D = DoG2(kernel_size, dance_direction_rad)

center = ceil(0.5 * [kernel_size kernel_size] );

[m1, m2] = getGaussMeans(dance_direction_rad, 6, center);

D = zeros(kernel_size);

R = [cos(dance_direction_rad) sin(dance_direction_rad); ...
    -sin(dance_direction_rad) cos(dance_direction_rad)];

S = R * [6 0; 0 2] * R';

for x = 1 : kernel_size
    for y = 1 : kernel_size
        D(y,x) = mvnpdf([x y], m1, S) - mvnpdf([x y], m2, S);
    end
end

D = D ./ max(max(D));

function [w1, w2] = getGaussMeans(dance_direction, peak_distance, center)
a   = dance_direction;
v   = [cos(a); sin(a)];
w1  = 0.5*peak_distance * [v(2) v(1)];
w2  = -w1 + center;
w1  = w1 + center;

function f = gauss1d(m, s, x)
f =  exp(-0.5 * ((x-m)/s)^2) / s*sqrt(2*pi);