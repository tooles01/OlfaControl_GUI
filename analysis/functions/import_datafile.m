%% import_datafile
% get datafile (.csv) from results folder, save in matlab folder as .mat file
% purpose is to speed up processing - don't need to re-import the whole thing every single time

% ***assumes current working directory is 'OlfaControl_GUI\analysis'

%%
% Inputs: 
%   - file name         (ex: '2022-09-13_datafile_02')
%   - file directory    (ex: 'C:\Users\Admin\Dropbox (NYU Langone Health)\OlfactometerEngineeringGroup (2)\Control\a_software\OlfaControl_GUI\result_files\48-line olfa\2022-09-13\')
% Output:
%   - saves .mat file to 'analysis\data files (raw)'
%   - returns cell array with the contents of the .mat file

%%
function this_mat_file_data = import_datafile(file_name, file_directory)
    dir_datafiles_matlab = strcat(pwd,'\','data files (raw)');
    dir_thisfile_full = strcat(dir_datafiles_matlab,'\',file_name,'.mat');
    
    % if .mat file does not exist yet, get the .csv and save it as a .mat file
    if ~isfile(dir_thisfile_full)
        
        dir_this_data_file = strcat(file_directory,file_name,'.csv');                           % full directory for this file
        raw_wholeFile = readcell(dir_this_data_file,'LineEnding',{'\r' '\n'},'Delimiter',',');  % read file & save to matlab folder
        
        %{
        if isfile(dir_thisfile_full)
            delete(dir_thisfile_full)   % make sure this file doesn't already exist (or else it gets in a weird endless loop)
        end
        %}
        save(dir_thisfile_full,"raw_wholeFile")     % save as .mat file
        this_mat_file_data = raw_wholeFile;
    else
        this_mat_file_data = load(dir_thisfile_full);
        this_mat_file_data = this_mat_file_data.raw_wholeFile;  % get the cell array from the struct
    end
end