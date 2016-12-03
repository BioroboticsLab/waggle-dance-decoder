function [ D ] = DoG3( kernel_size, m1, S1, m2, S2)
D = zeros(kernel_size, kernel_size);
for x = 1 : kernel_size
    for y = 1 : kernel_size
        D(y,x) = mvnpdf([x y], m1, S1) - mvnpdf([x y], m2, S2);
    end
end

end

