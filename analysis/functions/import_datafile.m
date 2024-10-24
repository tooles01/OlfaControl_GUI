%% import_datafile
% get datafile (*.csv) from results folder, save within analysis folder as *.mat file
% purpose is to speed up processing - don't need to re-import the whole *.csv every single time

% ***assumes current working directory is 'OlfaControl_GUI\analysis'

%%
% Inputs: 
%   - File name         (ex: '2022-09-13_datafile_02')
%   - File directory    (ex: 'C:\Users\Admin\Dropbox (NYU Langone Health)\OlfactometerEngineeringGroup (2)\Control\a_software\OlfaControl_GUI\result_files\48-line olfa\2022-09-13\')
% Output:
%   - Saves *.mat file to 'analysis\data files (raw)'
%   - Returns cell array with the contents of the *.mat file

%% ** NOTE FOR ME
% why do we have two imput variables instead of 1
% can't we just send the full directory over
% look into fixing this later

%%
function this_mat_file_data = import_datafile(file_name, file_directory)
    % Get path to this raw datafile (analysis\data files (raw)\file_name.mat)
    dir_rawdatafiles = strcat(pwd,'\','data files (raw)');
    dir_this_rawdatafile = strcat(dir_rawdatafiles,'\',file_name,'.mat');
    
    if ~isfile(dir_this_rawdatafile)
        % If *.mat file does not exist yet, get the *.csv (& save as a *.mat file)
        dir_this_datafile = strcat(file_directory,file_name,'.csv');                           % Full directory for this file
        raw_wholeFile = readcell(dir_this_datafile,'LineEnding',{'\r' '\n'},'Delimiter',',');  % Read file & save to matlab folder
        save(dir_this_rawdatafile,"raw_wholeFile")     % Save as .mat file
        this_mat_file_data = raw_wholeFile;
    else
        % If *.mat file already exists, load it in
        this_mat_file_data = load(dir_this_rawdatafile);
        this_mat_file_data = this_mat_file_data.raw_wholeFile;  % Get the cell array from the struct
    end
end