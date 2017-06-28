function A = loadData(datafilename)
fid = fopen(datafilename, 'r');
if fid == -1
    display('error while trying to open file')
end
A = fscanf(fid, '%f,%f,%f,%f,%d/%d/%d,%d:%d:%d:%d\n');
A = reshape(A, 11, length(A) / 11 )';

% convert frames to ms
A(:,1) = A(:,1)*10;

% convert timestamp to seconds, disregard milliseconds
A(:, 5) = A(:, 10) + 60*A(:, 9) + 3600*A(:, 8);

% throw away all irrelevant colums
A = A(:, [1:5 8:9]);

% convert angle: 0° should point upwards, positive should turn clockwise
%A(:,2) = mod( 2*pi + A(:,2) + pi/2, 2*pi);
% No need for this in 2016, the angles already comply with this convention

% add column that represents field direction

fclose(fid)