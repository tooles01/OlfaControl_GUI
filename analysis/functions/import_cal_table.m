%% import_cal_table
% get calibration table from results folder, save in matlab folder as .mat file
% purpose is to speed up processing - don't need to re-import the whole thing every single time

% ***assumes current working directory is 'OlfaControl_GUI\analysis'
% ***cal tables must be .txt files

%%
% Inputs: 
%   - file name         (ex: 'Honeywell_3100V')
%   - file directory    (ex: 'C:\Users\Admin\Dropbox (NYU Langone Health)\OlfactometerEngineeringGroup (2)\Control\a_software\OlfactometerControl\config\calibration_tables\')
% Output:
%   - saves .mat file to 'analysis\cal tables (imported)'
%   - returns cell array with the contents of the .mat file

%%
function this_cal_file_data = import_cal_table(file_name, file_directory)
    dir_cal_tables_matlab = strcat(pwd,'\','cal tables (imported)');
    dir_this_cal_table_matlab = strcat(dir_cal_tables_matlab,'\',file_name,'.mat');

    % if .mat file does not exist yet, get the .csv and save it as a .mat file
    if ~isfile(dir_this_cal_table_matlab)
        
        % try both .txt and .csv files
        try
            dir_this_cal_table = strcat(file_directory,file_name,'.txt');   % directory of the file to load
            this_cal_file_data = readmatrix(dir_this_cal_table);
        catch
            dir_this_cal_table = strcat(file_directory,file_name,'.csv');   % directory of the file to load
            this_cal_file_data = readmatrix(dir_this_cal_table);
        end

        this_cal_file_data(any(isnan(this_cal_file_data),2),:) = [];    % remove rows with nan vals        
        
        save(dir_this_cal_table_matlab,"this_cal_file_data")     % save as .mat file
    else
        this_cal_file_data = load(dir_this_cal_table_matlab);
        this_cal_file_data = this_cal_file_data.this_cal_file_data;  % get the cell array from the struct
    end
end