function D = DoG(kernel_size, dance_direction_rad)

center = ceil(0.5 * [kernel_size kernel_size] );

[m1, m2] = getGaussMeans(dance_direction_rad, 6, center);

D = zeros(kernel_size);

s = 2;

for x = 1 : kernel_size
    for y = 1 : kernel_size
        d1 = norm( m1 - [x y] );
        d2 = norm( m2 - [x y] );
        D(y,x) = normpdf(d1, 0, s) - normpdf(d2, 0, s);
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