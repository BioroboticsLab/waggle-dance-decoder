function [Performance] = process_images(IMGS)
A           = -90 : 90;
Performance = zeros(1, length(A));

for a = 1 : length(A)
    D           = DoG(13, A(a)*pi/180);
    img_last    = double( IMGS{1}(:,:,1) );
    img_int     = zeros(size(img_last));
    
    for i = 2 : length(IMGS)
        img_cur = double(IMGS{i}(:,:,1));

        img_diff = img_last - img_cur;

        img_diff = filter2([1 1 1; 1 1 1; 1 1 1]/9, img_diff);

        img_diff = filter2(D, img_diff);

        img_int = img_int + abs(img_diff);

%         imagesc(img_diff);
    %    
        img_last = img_cur;
    %     pause
    end
    
    fprintf('%d: %.2f\n', a, max(max(img_int)));
    Performance(a) = max(max(img_int));
end

imagesc(img_int);
surf(img_int)
   