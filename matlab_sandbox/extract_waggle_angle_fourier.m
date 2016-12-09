function a = extract_waggle_angle_fourier(IMGS)
img_last    = double( IMGS{1}(:,:,1) );
n           = size(img_last,1);
img_int     = zeros(n,n);
center      = [ceil(n/2) ceil(n/2)];

D           = fftshift(fft2(DoG3(n, center, 30*eye(2), center, 4*eye(2))));
imagesc(abs(D))


for i = 2 : length(IMGS)
    img_cur = double(IMGS{i}(:,:,1));
    img_diff = img_last - img_cur;
    img_diff = filter2([1 1 1; 1 1 1; 1 1 1]/9, img_diff);
%     FDI = abs((D .* fftshift(fft2(img_diff))));
    FDI = abs((fftshift(fft2(img_diff))));
    img_int = img_int + FDI;
    img_last = img_cur;
end

shapeInserter   = vision.ShapeInserter('Shape','Circles', 'Fill', true, 'FillColor', 'White');
circ_mask       = step(shapeInserter, zeros(size(img_int)), [26 26 6]);
img_int         = abs(D).*img_int .* circ_mask;
%
imagesc(img_int.^5);

[cv, theta] = imcov(img_int.^5);
[v d] = eig(cv);
a = atan2(v(2,2), v(1,2))*180/pi;

% angles = -90:90;
% q = [];
% for a = angles
% q = [q max(radon(img_int, a))];
% end
%
% [~, i] = max(q);
% a = angles(i);
