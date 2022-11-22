%% getSectionData.m

% Input:
%   - dataset (time, value) (time values must be in first column)
%   - start time
%   - end time

% Output:
%   - section of data within time valiues

%%
function sectionData = get_section_data(fullDataset,t1,t2)

idx_b = find(fullDataset(:,1)>=t1,1,'first');
idx_e = find(fullDataset(:,1)<=t2,1,'last');
sectionData = fullDataset(idx_b:idx_e,:);

end