function [ img_cov, theta ] = imcov( I )
m00 = immoments(I, 0, 0);
m11_ = immoments(I, 1, 1) / m00;
m02_ = immoments(I, 0, 2) / m00;
m20_ = immoments(I, 2, 0) / m00;
img_cov = [m20_ m11_; m11_ m02_];
theta = 0.5*atan(2*m11_ / (m20_ - m02_));
end

