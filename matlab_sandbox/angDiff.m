% d = angDiff(a1, a2, val_pi)
%
% returns the (smallest) difference d between two angles a1 and a2
% d is signed, i.e. the direction from a1 to a2 is encoded as well
% positive -> counter clockwise
% optionally pass an appropriate value for pi (180 if degrees) 
function d = angDiff(a1, a2, val_pi)


if nargin < 3
    val_pi = pi;
end
val_2pi = 2*val_pi;


d = mod((a1 - a2),val_2pi);

if (d > val_pi)
    d = d - val_2pi;
end
if (d < -val_pi)
    d = d + val_2pi;
end
d(d > val_pi) = -val_2pi + d(d > val_pi);
d(-d > val_pi) = val_2pi + d(-d > val_pi);
d = -d;