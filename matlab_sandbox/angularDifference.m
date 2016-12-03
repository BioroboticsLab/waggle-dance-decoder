function d = angularDifference(a1, a2)

%make a1, a2 -> [+180, -179]
a1 = mod(a1, 360);
a2 = mod(a2, 360);
if (a1 > 180)
    a1 = -360+a1;
end
if (a2 > 180)
    a2 = -360+a2;
end

d = absAngularDifference(a1,a2);

d(a1-a2 < 0) = -d(a1-a2 < 0);

d(abs(a1-a2)>180) = -d(abs(a1-a2)>180);
    
