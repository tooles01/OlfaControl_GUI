%% removeDuplicates_.m
% if there are duplicate entries for the same time value, average them

% **assumes data is already sorted

%%
%#ok<*AGROW>

%%
function newPdata = removeDuplicates_(pData)
    
    newPdata = pData;
    numVals = length(pData);
    [~,ind] = unique(pData(:,1),'rows','first');    % find unique values
    blankSet = 1:length(pData);
    dup_ind(:,1) = setdiff(blankSet,ind);           % find duplicate values
    
    %% if there are duplicate values:
    if ~isempty(dup_ind)

        % average duplicates & add to "newPData"; set the duplicate indices to Nan
        for i=1:length(dup_ind)
            idx_start = dup_ind(i)-1;       % duplicates start at 1-value
            time_0 = pData(idx_start,1);    % time value
            
            % if we haven't already done this one
            if ~isnan(newPdata(idx_start,1))
                valsToAvg = pData(idx_start,2);
                idx_next = idx_start+1;
                time_next = pData(idx_next,1);

                % while we increment & still have the same time value
                while time_0 == time_next

                    % if we're not at the end of the data, add it to valsToAvg
                    if idx_next <= numVals
                        valToAvg_next = pData(idx_next,2);
                        valsToAvg = [valsToAvg;valToAvg_next];
                        idx_next = idx_next+1;

                        % if we're not at the end of the data, check the next time value
                        if idx_next <= numVals
                            time_next = pData(idx_next,1);
                        else
                            break;
                        end

                    else
                        break;
                    end

                end

                % average values, add to newPdata
                val_avg = mean(valsToAvg);
                newPdata(idx_start,1) = time_0;
                newPdata(idx_start,2) = val_avg;

                % set the spaces we removed to "NaN" (to pull out after)
                j_beg = idx_start+1;
                j_end = idx_next-1;
                for j=j_beg:j_end
                    newPdata(j,:) = NaN;
                end
            end

        end

    end
    
    %% remove Nans
    nan_idx = all(~isnan(newPdata),2);
    newPdata = newPdata(nan_idx,:);

end