
kernel_size = 50;
m = kernel_size/2 + 1;
dance_direction_rad = 90*pi/180;

D = zeros(kernel_size);

R = [cos(dance_direction_rad) sin(dance_direction_rad); ...
    -sin(dance_direction_rad) cos(dance_direction_rad)];

S = R * [6 0; 0 2] * R';


for x = 1 : kernel_size
    for y = 1 : kernel_size
        D(y,x) = mvnpdf([x y], m, S);
    end
end

imagesc(D)

[cv, th] = imcov(D)

[v d] = eig(cv)

th*180/pi

atan2(v(2,2), v(1,2))*180/pi