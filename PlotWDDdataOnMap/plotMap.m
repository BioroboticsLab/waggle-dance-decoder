function plotMap(mapfilename, datafilename)

%Hardcoded for an specific image map
px_per_meter = 321 / 100;
%meter_per_ms = 235 / 440; % see (Landgraf et al. 2011)
meter_per_ms = 342 / 570;

% Hive image coordinate
HL = [2190, 1540];
% Feeder image coordinate
FL = [1470, 2370];
% Angle hive-feeder in rad

% Distance hive-feeder in pixels
DHF = sqrt((HL(1)-FL(1))^2 + (HL(2)-FL(2))^2);
DHF

%Angle hive-feeder
AHF = atan2((HL(1)-FL(1)),-(HL(2)-FL(2))) + pi/2;
AHF

% read in raw data
A = loadData(datafilename);

% azimuth translation and angle conversion to normality (0° is on x-axis
% and rotates counter-clockwise???)
A = translateToRelativeSunDirection(A);

% conversion to meters
A(:,2) = meter_per_ms * A(:,2); 

% conversion to pixels
A(:,2) = px_per_meter * A(:,2);

%Mean dance orientation
a = circMean(-A(:,3));
a

%Error average angle to AHF
v1 = [cos(AHF),sin(AHF)];
v2 = [cos(a),sin(a)];
directionError = acos(dot(v1,v2))

close all
h = imshow(mapfilename)
hold on

% to plot each cluster in an intensity level, deppending on the number of WRs
col_hsv = ones(length(A),3);
col_hsv(:,1) = col_hsv(:,1)*0.8;
col_hsv(:,2) = (A(:,6)-min(A(:,6)))/(max(A(:,6))-min(A(:,6)));
col_rgb = hsv2rgb(col_hsv);

%Orientation and duration of WR are translated to image coordinates
Temp = [A(:,2).*cos(-A(:,3))+ HL(1), A(:,2).* sin(-A(:,3))+ HL(2), col_rgb];

%Only advertised locations within the image coordinates are ploted
count = 1;
for i = 1:length(Temp)
    if (Temp(i,1) > 20 && Temp(i,2) > 20 && Temp(i,1) < 4573 && Temp(i,2) < 3080)        
        P(count,:) = Temp(i,:);
        count = count + 1;
    end
end

%All advertised locations
scatter (P(:, 1), P(:, 2),20,P(:,3:5),'filled', ...                                                
                                                'MarkerEdgeColor',[1 1 1],...
                                                'LineWidth',0.1);                                            
%Hive location
plot( HL(1), HL(2), '^',    'MarkerEdgeColor','k', ...
                                                'MarkerFaceColor','w', ...
                                                'MarkerSize',6, ...
                                                'LineSmoothing', 'on', ...
                                                'LineWidth',0.1);
%Average orientation
plot( [0 DHF*cos(a)*1.85]+ HL(1), [0 DHF*sin(a)*1.85]+ HL(2), '--', ...
                                                'Color', [.75 0 .75], ...
                                                'LineWidth',0.5, ...
                                                'LineSmoothing','on')
% %Real orientation
% plot( [0 DHF*cos(AHF)*1.85]+ HL(1), [0 DHF*sin(AHF)*1.85]+ HL(2), '--', ...
%                                                 'Color', [1 0 0], ...
%                                                 'LineWidth',0.5, ...
%                                                 'LineSmoothing','on')
%Food source location                                            
plot( FL(1), FL(2), 'd',  'MarkerEdgeColor','k', ...
                                                'MarkerFaceColor','g', ...
                                                'MarkerSize',6, ...
                                                'LineSmoothing', 'on', ...
                                                'LineWidth',0.1);

%print('bla','-dpng','-r600')