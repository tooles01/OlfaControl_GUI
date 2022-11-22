%% int_to_SCCM.m
% convert olfactometer data from ints to sccm vals

% Input:
%   - data to convert: matrix of doubles (time, value)
%   - conversion table: matrix of doubles (sccm, arduinoInt)
%   - which column to convert
% Output:
%   - data converted (time, value)

% do the same linear interpolation you do in python
%% ***cal table must be in order

function data_sccm = int_to_SCCM(data_raw,cal_table,~)
    cal_table_sccm = cal_table(:,1);
    cal_table_ints = cal_table(:,2);
    min_ard_val = min(cal_table_ints);
    max_ard_val = max(cal_table_ints);
    
    data_sccm(:,1) = data_raw(:,1); % copy over the time values
    for i=1:height(data_raw)
        val_int = data_raw(i,2);
        % if greater than the max, set it to the max
        if val_int > max_ard_val
            val_sccm = max(cal_table_sccm);
        % if less than the min, set it to the min
        elseif val_int < min_ard_val
            val_sccm = min(cal_table_sccm);
        % if in the dictionary, get that value
        elseif ismember(val_int,cal_table_ints)
            val_sccm = cal_table_sccm(val_int==cal_table_ints);
        else
            val_sccm = interp1(cal_table_ints,cal_table_sccm,val_int);
        end
        data_sccm(i,2) = val_sccm;
    end
end
