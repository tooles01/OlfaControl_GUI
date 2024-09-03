%% removeDuplicates_.m
% If there are duplicate entries for the same time value, average them

% **assumes data is already sorted

%%
%#ok<*AGROW>

function newPdata = removeDuplicates_(pData)
    newPdata = pData;
    numVals = length(pData);

    % Find unique values
    [~,ind] = unique(pData(:,1),'rows','first');
    blankSet = 1:length(pData);
    % Find indices of duplicate time values
    dup_ind(:,1) = setdiff(blankSet,ind);
    
    %% If there are duplicate values:
    if ~isempty(dup_ind)
        % Average duplicates & add to "newPData"; set the duplicate indices to Nan
        
        % For each duplicate value
        for i=1:length(dup_ind)
            idx_start = dup_ind(i)-1;       % Index of the (first) duplicate value
            time_0 = pData(idx_start,1);    % Time value here
            
            % If we haven't already done this one
            if ~isnan(newPdata(idx_start,1))
                valsToAvg = pData(idx_start,2);
                idx_next = idx_start+1;
                time_next = pData(idx_next,1);  % This should be the same since it's a duplicate lol

                % While we increment & still have the same time value
                while time_0 == time_next

                    % If we're not at the end of the data, add column2 value to valsToAvg
                    if idx_next <= numVals
                        valToAvg_next = pData(idx_next,2);
                        valsToAvg = [valsToAvg;valToAvg_next];
                        idx_next = idx_next+1;

                        % If we're not at the end of the data, check if the next time value is also a duplicate
                        if idx_next <= numVals
                            time_next = pData(idx_next,1);
                        else
                            break;
                        end

                    else
                        break;
                    end

                end

                % Average the values, add to newPdata
                val_avg = mean(valsToAvg);
                newPdata(idx_start,1) = time_0;
                newPdata(idx_start,2) = val_avg;

                % Set the extra (duplicate) data points to "NaN" (to pull out after)
                j_beg = idx_start+1;
                j_end = idx_next-1;
                for j=j_beg:j_end
                    newPdata(j,:) = NaN;
                end
            end

        end

    end
    
    %% Remove Nans
    nan_idx = all(~isnan(newPdata),2);
    newPdata = newPdata(nan_idx,:);

end