library(tidyverse)

# This is PURELY to make pretty charts. No real analysis is happening here, and most of the charts can be easily
# reproduced in zebrafishanalysis

# NOTE ON COLOURS: We use the safe colourblind palette described in rcartocolor
# (https://github.com/Nowosad/rcartocolor)

safe_colorblind_palette <- c("#88CCEE", "#CC6677", "#DDCC77", "#117733", "#332288", "#AA4499", 
                             "#44AA99", "#999933", "#882255", "#661100", "#6699CC", "#888888")

scales::show_col(safe_colorblind_palette)


full_data <- read.csv("all_fish_by_fish.csv")

ggplot(data = full_data) +
  geom_col(mapping = aes(x = X, y = d2))


file_list <- list.files(pattern="export_\\d+.csv")

period_data <- as_tibble(do.call(rbind, lapply(file_list, function(x) cbind(read.csv(x), period=strtoi(str_extract(x, "[0-9]+"))))))
theme_set(theme_bw()) 
period_data %>% 
  arrange(period) %>% 
    ggplot() +
      geom_boxplot(mapping = aes(x = as.factor(period), y = d2)) +
      labs(title="Exploration Index by 5 minute interval",
           x = "Slice start time (s)",
           y = "Discrimination index (d2)")

period_data %>% 
  arrange(period) %>% 
  ggplot() +
  geom_line(mapping = aes(x = period, y = d2, color = X)) +
  labs(title="Relative index of exploration by 5 minute interval")

# Accelerations comparisons

same_obj_a <- read.csv("same_obj_a_acc.csv", header = FALSE, colClasses = c("V1"="double"))
same_obj_b <- read.csv("same_obj_b_acc.csv", header = FALSE, colClasses = c("V1"="double"))
diff_obj_a <- read.csv("diff_obj_a_acc.csv", header = FALSE, colClasses = c("V1"="double"))
diff_obj_b <- read.csv("diff_obj_b_acc.csv", header = FALSE, colClasses = c("V1"="double"))


colours_accs <- c("Training: Left Object" = safe_colorblind_palette[2],
            "Training: Right Object" = safe_colorblind_palette[8], 
            "Testing: Familiar Object" = safe_colorblind_palette[4],
            "Testing: Novel Object" = safe_colorblind_palette[10])

# This is plotting the RAW VALUES. This is bad, as object preferences will mess with the data!
ggplot() +
  geom_freqpoly(aes(V1, color = "Training: Left Object"), data=same_obj_a, size = 1.0) +
  geom_freqpoly(aes(V1, color = "Training: Right Object"), data=same_obj_b, size = 1.0) +
  geom_freqpoly(aes(V1, color = "Testing: Familiar Object"), data=diff_obj_a, size = 1.0) +
  geom_freqpoly(aes(V1, color = "Testing: Novel Object"), data=diff_obj_b, size = 1.0) +
  ggtitle("Accelerations near objects", ) +
  labs(x = "Acceleration (pixels/s^2)",
       y = "Count",
       color = "Legend") +
  scale_color_manual(values = colours_accs)

ggplot() +
  geom_density(aes(V1, color = "Training: Left Object", fill = "Training: Left Object")
               , data=same_obj_a, alpha = 0.4, lwd = 0.8, adjust = 0.5)+
  geom_density(aes(V1, color = "Training: Right Object", fill = "Training: Right Object")
               , data=same_obj_b, alpha = 0.4, lwd = 0.8, adjust = 0.5) +
    geom_density(aes(V1, color = "Testing: Familiar Object", fill = "Testing: Familiar Object")
                , data=diff_obj_a, alpha = 0.4, lwd = 0.8, adjust = 0.5) +
    geom_density(aes(V1, color = "Testing: Novel Object", fill = "Testing: Novel Object")
                 , data=diff_obj_b, alpha = 0.4, lwd = 0.8, adjust = 0.5)
  
