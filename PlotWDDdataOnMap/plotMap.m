function plotMap(mapfilename, datafilename)

%Hardcoded for an specific image map
px_per_meter = 321 / 100;
meter_per_ms = 235 / 440; % see (Landgraf et al. 2011)

% Hive and feeder image coordinate
hiveLocation = [2190, 1540];
feederLocation = [1470, 2370];

% read in raw data
A = loadData(datafilename);
A

% azimuth translation and angle conversion to normality (0° is on x-axis
% and rotates counter-clockwise)
A = translateToRelativeSunDirection(A);

% conversion to meters
A(:,2) = meter_per_ms * A(:,2); 

% conversion to pixels
A(:,2) = px_per_meter * A(:,2);

close all
h = imshow(mapfilename)
hold on


P = [A(:,2) .* cos( -A(:,3)  ) + hiveLocation(1), A(:,2) .* sin( -A(:,3) ) + hiveLocation(2)];

meanDanceLocationWeighted = [ mean( A(:,6) .* P(:, 1) ), mean( A(:,6) .* P(:, 2) )];


a = circMean(-A(:,3));
plot( [0 1000*cos(a)]+ hiveLocation(1), [0 1000*sin(a)]+ hiveLocation(2), '--', ...
                                                'Color', [.75 0 .75], ...
                                                'LineWidth',0.5, ...
                                                'LineSmoothing','on')

plot( hiveLocation(1), hiveLocation(2), '^',    'MarkerEdgeColor','k', ...
                                                'MarkerFaceColor','w', ...
                                                'MarkerSize',8, ...
                                                'LineSmoothing', 'on', ...
                                                'LineWidth',0.1);
                                            
plot( P(:, 1), P(:, 2), 'o',   'MarkerEdgeColor','w', ...
                                                'MarkerFaceColor','m', ...
                                                'MarkerSize',5, ...
                                                'LineSmoothing', 'on', ...
                                                'LineWidth',0.1);

plot( meanDanceLocationWeighted(1), meanDanceLocationWeighted(2), 'o',   'MarkerEdgeColor','w', ...
                                                'MarkerFaceColor','b', ...
                                                'MarkerSize',6, ...
                                                'LineSmoothing', 'on', ...
                                                'LineWidth',0.1);


plot( feederLocation(1), feederLocation(2), 'd',  'MarkerEdgeColor','k', ...
                                                'MarkerFaceColor','g', ...
                                                'MarkerSize',6, ...
                                                'LineSmoothing', 'on', ...
                                                'LineWidth',0.1);

