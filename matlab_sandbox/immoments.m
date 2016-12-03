function [ m ] = immoments( I, p, q)
img_size    = size(I);
center      = img_size/2+1; 

x = 1:img_size(2);
y = 1:img_size(1);

X = ((x - center(2)).^p);
Y = ((y - center(1)).^q);

m = sum(sum((X' * Y) .* I));
end

