
input_folder = 'C:\Users\שחר\Desktop\all';
output_folder = 'C:\Users\שחר\Desktop\data';


achromat_folder = 'C:\Users\שחר\Desktop\achromat_all';
achromat_files = dir(fullfile(achromat_folder, '*.csv'));


[~, folder_name] = fileparts(input_folder);


files = dir(fullfile(input_folder, '*.csv'));


T_all = table();


for idx = 1:length(files)
    filename = fullfile(input_folder, files(idx).name);

    % Read CSV with date handling
    opts = detectImportOptions(filename);
    datetimeVars = opts.VariableNames(contains(opts.VariableTypes, 'datetime'));
    for k = 1:length(datetimeVars)
        opts = setvaropts(opts, datetimeVars{k}, 'InputFormat', 'MM/dd/yyyy HH:mm');
    end
    T = readtable(filename, opts);

    
    rows_to_keep = ~cellfun(@isempty, T.saturation_pattern) & ~cellfun(@isempty, T.color_scheme);
    indices = find(rows_to_keep);

    
    AE = T.saturation_pattern(indices);
    AC = T.color_scheme(indices);
    Z = T.response(indices);

    
    for i = 1:length(Z)
        if ismissing(Z(i)) && indices(i) < height(T)
            Z(i) = T.response(indices(i) + 1);
        end
    end

    
    file_label = repmat({files(idx).name}, length(Z), 1);
    T_current = table(file_label, AE, AC, Z, ...
        'VariableNames', {'file_name', 'saturation_pattern', 'color_scheme', 'response'});

    
    T_current.saturation_pattern = strtrim(string(T_current.saturation_pattern));
    T_current.color_scheme = strtrim(string(T_current.color_scheme));
    [~, unique_idx] = unique(T_current(:, {'saturation_pattern', 'color_scheme'}), 'rows', 'stable');
    T_current = T_current(unique_idx, :);

    
    if height(T_current) ~= 12
        warning(' File %s has %d rows after filtering – expected exactly 12.', ...
                 files(idx).name, height(T_current));
    end

    
    T_all = [T_all; T_current];
end


output_filename = fullfile(output_folder, [folder_name '_all_fix.csv']);
writetable(T_all, output_filename);
fprintf(' Merged CSV saved to: %s\n', output_filename);



T_all.saturation_pattern = strtrim(string(T_all.saturation_pattern));
T_all.color_scheme = strtrim(string(T_all.color_scheme));


correct_answers = containers.Map( ...
    {'100-70-40-10','10-40-70-100','100-70-70-10','10-70-70-100','100-40-40-10','10-40-40-100'}, ...
    [1, 0, 1, 0, 1, 0]);

patterns = string(keys(correct_answers));

colors = string({'orange', 'purple'});

results = zeros(length(patterns), length(colors));
for i = 1:length(patterns)
    for j = 1:length(colors)
        rows = T_all.saturation_pattern == patterns(i) & ...
               T_all.color_scheme == colors(j);
        correct_val = correct_answers(char(patterns(i)));
        relevant = T_all.response(rows);
        correct_count = sum(relevant == correct_val);
        total_count = sum(~ismissing(relevant));
        fprintf('✔ %s / %s → %d out of %d correct\n', ...
            patterns(i), colors(j), correct_count, total_count);
        if total_count > 0
            results(i,j) = correct_count / total_count;
        else
            results(i,j) = NaN;
        end
    end
end

new_order = [
    "10-40-70-100";
    "100-70-40-10";
    "10-40-40-100";
    "10-70-70-100";
    "100-40-40-10";
    "100-70-70-10"
];

[~, idx_order] = ismember(new_order, patterns);
patterns = patterns(idx_order);
results = results(idx_order, :); 


achromat_map = containers.Map( ...
    {'10-40-40-100', '10-70-70-100', '100-40-40-10', ...
     '100-70-70-10', '100-70-40-10', '10-40-70-100'}, ...
    { {'snake_illusion_p35_c707070-ffffff-ffffff-000000_s0-0-0-0_w1.0-1.0-1.0-1.0_a-15.5_bg-808080.png', 0}, ...
      {'snake_illusion_p35_c707070-ffffff-ffffff-000000_s0-0-0-0_w1.0-1.0-1.0-1.0_a-15.5_bg-808080.png', 0}, ...
      {'snake_illusion_p35_c000000-ffffff-ffffff-707070_s0-0-0-0_w1.0-1.0-1.0-1.0_a-15.5_bg-808080.png', 1}, ...
      {'snake_illusion_p35_c000000-ffffff-ffffff-707070_s0-0-0-0_w1.0-1.0-1.0-1.0_a-15.5_bg-808080.png', 1}, ...
      {'snake_illusion_p35_c000000-B0B0B0-FFFFFF-707070_s0-0-0-0_w1.0-1.0-1.0-1.0_a-15.5_bg-808080.png', 1}, ...
      {'snake_illusion_p35_c707070-ffffff-b0b0b0-000000_s0-0-0-0_w1.0-1.0-1.0-1.0_a-15.5_bg-808080.png', 0} ...
    });

achromat_counts = containers.Map();
achromat_totals = containers.Map();

for file = achromat_files'
    fname = fullfile(achromat_folder, file.name);
    opts = detectImportOptions(fname);
    T = readtable(fname, opts);

    if ~ismember('actual_filename', T.Properties.VariableNames) || ...
       ~ismember('response', T.Properties.VariableNames)
        continue;
    end

    T.image = strtrim(string(T.actual_filename));
    T.response = T.response;

    for i = 1:length(patterns)
        pattern = patterns(i);
        if ~isKey(achromat_map, pattern)
            continue;
        end

        info = achromat_map(pattern);
        image_name = info{1};
        correct_val = info{2};

        rows = contains(T.image, image_name);
        relevant = T.response(rows);

        correct_count = sum(relevant == correct_val);
        total_count = sum(~ismissing(relevant));

        if total_count > 0
            if ~isKey(achromat_counts, pattern)
                achromat_counts(pattern) = 0;
                achromat_totals(pattern) = 0;
            end
            achromat_counts(pattern) = achromat_counts(pattern) + correct_count;
            achromat_totals(pattern) = achromat_totals(pattern) + total_count;
        end
    end
end

achromat_results = NaN(length(patterns), 1);
for i = 1:length(patterns)
    pattern = patterns(i);
    if isKey(achromat_totals, pattern) && achromat_totals(pattern) > 0
        achromat_results(i) = achromat_counts(pattern) / achromat_totals(pattern);
        fprintf('✔ Achromat %s → %d out of %d correct\n', ...
            pattern, achromat_counts(pattern), achromat_totals(pattern));
    end
end



figure;
b1 = bar(results, 'grouped');
b1(1).FaceColor = [1, 0.5, 0];    % orange
b1(2).FaceColor = [0.5, 0, 0.7];  % purple
combined_std = std(results, 1, 2);  % std לפי שורות

for i = 1:numel(b1)
    x = b1(i).XEndPoints;
    y = b1(i).YEndPoints;
    labels = string(round(b1(i).YData, 2));
    text(x, y + 0.03, labels, 'HorizontalAlignment', 'center', ...
        'FontSize', 10, 'FontWeight', 'bold');
end
% הוספת error bars לכתום בלבד – סטיית תקן של הצמד (כתום וסגול)
hold on;

% על עמודות כתומות
x_err1 = b1(1).XEndPoints;
y_err1 = b1(1).YEndPoints;
errorbar(x_err1, y_err1, combined_std, 'k.', 'CapSize', 8, 'LineWidth', 1.2);

% על עמודות סגולות
x_err2 = b1(2).XEndPoints;
y_err2 = b1(2).YEndPoints;
errorbar(x_err2, y_err2, combined_std, 'k.', 'CapSize', 8, 'LineWidth', 1.2);


xticklabels(patterns);
xtickangle(45);
ylim([0 1.05]);
ylabel('Proportion of Correct Responses');
legend(colors, 'Location', 'northeast');
title('Success Rate by Pattern and Color');
grid on;

grouped_plot_filename = fullfile(output_folder, [folder_name '_success_rate_plot_grouped.png']);
saveas(gcf, grouped_plot_filename);
fprintf('📊 Grouped plot saved to: %s\n', grouped_plot_filename);

flat_patterns = repmat(patterns, 1, numel(colors));
flat_colors = repelem(colors, numel(patterns));
flat_values = results(:);
xticks_labels = strcat(flat_patterns, " / ", flat_colors);

color_rgb_map = containers.Map(...
    {'orange', 'purple'}, {[1, 0.5, 0], [0.5, 0, 0.7]});
bar_colors = zeros(length(flat_colors), 3);
for i = 1:length(flat_colors)
    bar_colors(i, :) = color_rgb_map(char(flat_colors(i)));
end

figure;
b2 = bar(flat_values, 'FaceColor', 'flat');
b2.CData = bar_colors;

for i = 1:length(flat_values)
    if ~isnan(flat_values(i))
        text(i, flat_values(i) + 0.03, sprintf('%.2f', flat_values(i)), ...
            'HorizontalAlignment', 'center', 'FontSize', 10, 'FontWeight', 'bold');
    end
end

xticklabels(xticks_labels);
xtickangle(45);
ylim([0 1.05]);
ylabel('Proportion of Correct Responses');
title('Success Rate per Pattern/Color Combination');
grid on;

flat_plot_filename = fullfile(output_folder, [folder_name '_success_rate_plot_flat.png']);
saveas(gcf, flat_plot_filename);
fprintf('📊 Flat plot saved to: %s\n', flat_plot_filename);


combined_std = zeros(length(patterns), 1);
for i = 1:length(patterns)
    orange_val = results(i, colors == "orange");
    purple_val = results(i, colors == "purple");
    combined_std(i) = std([orange_val, purple_val], 1);  
end

figure;
hold on;
b = bar(results, 'grouped');
b(1).FaceColor = [1, 0.5, 0];    % orange
b(2).FaceColor = [0.5, 0, 0.7];  % purple

group_width = min(0.8, size(results,2)/(size(results,2)+1.5));
x = zeros(length(patterns), 1);
for i = 1:length(patterns)
    x(i) = i;
end

errorbar(x - group_width/4, results(:,1), combined_std, 'k.', 'CapSize', 8, 'LineWidth', 1.2);
errorbar(x + group_width/4, results(:,2), combined_std, 'k.', 'CapSize', 8, 'LineWidth', 1.2);

xticks(x);
xticklabels(patterns);
xtickangle(45);
ylim([0 1.2]);
ylabel('Proportion of Correct Responses');
legend(colors, 'Location', 'northeast');
title(['Success Rate by Pattern and Color (Combined STD) - ' folder_name]);
grid on;
hold off;

combined_std_filename = fullfile(output_folder, [folder_name '_success_rate_combined_std.png']);
saveas(gcf, combined_std_filename);
fprintf('📊 Combined STD plot saved to: %s\n', combined_std_filename);

flipped_pairs = {
    "10-40-40-100", "100-40-40-10";
    "10-70-70-100", "100-70-70-10";
    "10-40-70-100", "100-70-40-10"
};

pair_labels = {};
bar_data = [];
bar_colors = [];
std_errors = [];

for c = 1:length(colors)
    col = colors(c);  % "orange" or "purple"
    for p = 1:size(flipped_pairs,1)
        pat1 = flipped_pairs{p,1};
        pat2 = flipped_pairs{p,2};

        val1 = results(patterns == pat1, colors == col);
        val2 = results(patterns == pat2, colors == col);

        bar_data = [bar_data; val1, val2];
        std_errors = [std_errors; std([val1, val2], 1)];
        pair_labels = [pair_labels; strcat(pat1, "/", pat2)];
        bar_colors = [bar_colors; repmat(col, 1, 2)];
    end
end

figure;
hold on;

x = 1:size(bar_data,1);  % Each pair
width = 0.35;

b1 = bar(x - width/2, bar_data(:,1), width, 'FaceColor', 'flat');
b2 = bar(x + width/2, bar_data(:,2), width, 'FaceColor', 'flat');

for i = 1:size(bar_data,1)
    col_rgb = color_rgb_map(char(bar_colors(i,1)));
    b1.CData(i,:) = col_rgb;
    b2.CData(i,:) = col_rgb;
end

errorbar(x - width/2, bar_data(:,1), std_errors, 'k.', 'CapSize', 6, 'LineWidth', 1.2);
errorbar(x + width/2, bar_data(:,2), std_errors, 'k.', 'CapSize', 6, 'LineWidth', 1.2);

xticks(x);
xticklabels(pair_labels);
xtickangle(45);
ylim([0 1.2]);
ylabel('Proportion of Correct Responses');
title(['Flipped Pattern Pairs - Same Color ±STD - ' folder_name]);
grid on;


flipped_std_filename = fullfile(output_folder, [folder_name '_flipped_pairs_same_color_std.png']);
saveas(gcf, flipped_std_filename);
fprintf('📊 Flipped pairs plot saved to: %s\n', flipped_std_filename);




figure;
hold on;

bar_colors = {[1, 0.5, 0], [0.5, 0, 0.7], [0, 0, 0]};
labels = {'Orange', 'Purple', 'A-Chromatic'};

b = bar(results_with_achromat, 'grouped');

for i = 1:numel(b)
    b(i).FaceColor = bar_colors{i};
end

for i = 1:numel(b)
    x_vals = b(i).XEndPoints;
    y_vals = b(i).YEndPoints;
    labels_text = string(round(b(i).YData, 2));
    text(x_vals, y_vals + 0.03, labels_text, ...
        'HorizontalAlignment', 'center', 'FontSize', 9, 'FontWeight', 'bold');
end

xticks(1:length(patterns));
xticklabels(patterns);
xtickangle(45);
ylim([0 1.1]);
ylabel('Proportion of Correct Responses');
legend(labels, 'Location', 'northeast');
title(['Success Rate by Pattern: Orange vs Purple vs Achromat - ' folder_name]);
grid on;

fifth_plot = fullfile(output_folder, [folder_name '_success_rate_achromat.png']);
saveas(gcf, fifth_plot);
fprintf('📊 Fifth plot (Achromat) saved to: %s\n', fifth_plot);


figure;
hold on;

bar_colors = {[1, 0.5, 0], [0.5, 0, 0.7], [0, 0, 0]};
labels = {'Orange', 'Purple', 'A-Chromatic'};

values_for_std = results_with_achromat;

results_plot = results_with_achromat;
results_plot(isnan(results_plot)) = 0;

b = bar(results_plot, 'grouped');

for i = 1:numel(b)
    b(i).FaceColor = bar_colors{i};
end

std_vals = NaN(size(results_with_achromat));
for i = 1:size(results_with_achromat,1)
    vals = results_with_achromat(i,:);
    std_val = std(vals(~isnan(vals)), 1);
    for j = 1:3
        if ~isnan(results_with_achromat(i,j))
            std_vals(i,j) = std_val;
        end
    end
end

for i = 1:numel(b)
    x_vals = b(i).XEndPoints;
    y_vals = b(i).YEndPoints;
    err = std_vals(:,i);
    errorbar(x_vals, y_vals, err, 'k.', 'CapSize', 8, 'LineWidth', 1.2);
end

for i = 1:numel(b)
    x_vals = b(i).XEndPoints;
    y_vals = b(i).YEndPoints;
    labels_text = strings(size(y_vals));
    for j = 1:length(y_vals)
        if isnan(values_for_std(j,i))
            labels_text(j) = "N/A";
        else
            labels_text(j) = sprintf('%.2f', values_for_std(j,i));
        end
    end
    for i = 1:numel(b)
       x_vals = b(i).XEndPoints;
       y_vals = b(i).YEndPoints;
       labels_text = strings(size(y_vals));
          for j = 1:length(y_vals)
              val = values_for_std(j,i);
              std_val = std_vals(j,i);
              if isnan(val)
                   labels_text(j) = "N/A";
              else
                   labels_text(j) = sprintf('%.2f\n±%.2f', val, std_val);
              end
         end
         text(x_vals, y_vals + 0.03, labels_text, ...
           'HorizontalAlignment', 'center', 'FontSize', 9, ...
           'FontWeight', 'bold', 'VerticalAlignment', 'bottom');
   end

end

xticks(1:length(patterns));
xticklabels(patterns);
xtickangle(45);
ylim([0 1.2]);
ylabel('Proportion of Correct Responses ± STD');
legend(labels, 'Location', 'northeast');
title(['Success Rate by Pattern with STD - ' folder_name]);
grid on;

sixth_plot = fullfile(output_folder, [folder_name '_success_rate_std_plot.png']);
saveas(gcf, sixth_plot);
fprintf('📊 Sixth plot (with STD) saved to: %s\n', sixth_plot);


