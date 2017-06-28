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
% discard short waggles and short dances
A = filterData(A);

% azimuth translation and angle conversion to normality (0° is on x-axis
% and rotates counter-clockwise)
A = translateToRelativeSunDirection(A);

% conversion to meters
A(:,1) = meter_per_ms * A(:,1); 

% conversion to pixels
A(:,1) = px_per_meter * A(:,1);

close all
h = imshow(mapfilename)
hold on


P = [A(:,1) .* cos( -A(:,2)  ) + hiveLocation(1), A(:,1) .* sin( -A(:,2) ) + hiveLocation(2)];

meanDanceLocationWeighted = [ mean( A(:,5) .* P(:, 1) ), mean( A(:,5) .* P(:, 2) )];


a = circMean(-A(:,2));
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
% plot( mean(P(:,1)), mean(P(:,2)), 'ro' )
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

