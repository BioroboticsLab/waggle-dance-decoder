
q = [0 0 0 0 0];
for i = 1 : size(A, 1)
    
    DD = A(i, 3:end);
    DD(DD==0) = [];
    DD = reshape(DD, 2, length(DD)/2)';
    DD(:,2) = 100 - DD(:,2);    
    
    Nhalbe = floor(length(DD)/2);
    m = mean(DD);
    m1 = mean(DD(1:Nhalbe, :));
    m2 = mean(DD(Nhalbe+1:end, :));
    
    a1 = A(i, 1) * pi / 180;
    a2 = A(i, 2) * pi / 180;
    
    dDD = diff(DD);
    dDD2 = [DD(:,1) - m1(1,1) DD(:,2)-m1(1,2)];
    
    feat1 = dDD2 * [cos(a2) sin(a2)]';
       
    feat2 = atan2(dDD2(:,2), dDD2(:,1));
    [n, c] = hist(feat2);    
    
    maxima = sort(n);
    maxima = maxima(end-1 : end);
    
    a3 = circ_mean(c(n==max(n))');
    
    f4 = ((m2-m1) + [cos(a3) sin(a3)]);
    
    v1 = m + 5*[cos(a1) sin(a1)]; % ground truth direction
    v2 = m + 5*[cos(a2) sin(a2)]; % decoder direction
    v3 = m + m2-m1;          % feature direction
    v4 = m + 5*[cos(a3) sin(a3)]; % feature direction
    
    
    q0 = [cos(a1) sin(a1)] *[cos(a2) sin(a2)]' >0; % does gt match decoder
    q1 = f4  *[cos(a1) sin(a1)]' >0; %does feature match gt direction
    q2 = f4  *[cos(a2) sin(a2)]' >0; % does feature match decoder direction
    q3 = ([cos(a2+(q2-1)*pi) sin(a2+(q2-1)*pi)]*[cos(a1) sin(a1)]') >0; % does use of feature flip dec dir to gt dir
%     
    dd_area = (max(DD(:,2))-min(DD(:,2))) * (max(DD(:,2))-min(DD(:,2)));

    if dd_area < 4
        continue
    end
    
    [q0 q1 q2 q3 dd_area]
  
    
    q = q + [1 q0 q1 q2 q3];
    
    subplot(2,1,1)
    
    plot([m(1) v1(1)], [m(2) v1(2)], 'g')
    hold on
    plot([m(1) v2(1)], [m(2) v2(2)], 'b')
    plot([m(1) v3(1)], [m(2) v3(2)], 'r')
    plot([m(1) v4(1)], [m(2) v4(2)], 'm')
    
    plot(DD(:,1), DD(:,2), '-*')
    plot(DD(1,1), DD(1,2), 'g*')
    plot(DD(end,1), DD(end,2), 'r*')
    
    hold off
    axis equal
  
    
    subplot(2,1,2)
    hist(feat2)
    
    
    
%     pause
end
