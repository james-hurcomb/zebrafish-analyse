setwd("~/Documents/zebrafish-analyse/stats_scripts")
library(tidyverse)
library(grid)
library(gtable)    
library(gridExtra)
library(reshape)
require(png)
library(ggpubr)
library(rstatix)
library(forcats)
library(data.table)
options(scipen=20000)

# This is PURELY to make pretty charts. No real analysis is happening here, and most of the charts can be easily
# reproduced in zebrafishanalysis

# NOTE ON COLOURS: We use the safe colourblind palette described in rcartocolor
# (https://github.com/Nowosad/rcartocolor)

safe_colorblind_palette <- c("#88CCEE", "#CC6677", "#DDCC77", "#117733", "#332288", "#AA4499", 
                             "#44AA99", "#999933", "#882255", "#661100", "#6699CC", "#888888")
# Little visualisation so I can see what colour is which when I decide what to colour my charts
scales::show_col(safe_colorblind_palette)

# LOAD AND MEDDLE WITH DATA

full_data_m_1 <- read.csv("all_fish_by_fish.csv")
full_data_m_2 <- read.csv("two_month_fish_measures.csv")

full_data_m_1 %>% 
  summarise_at(c("d1", "d2", "d3"), sd)

full_data_m_2 %>% 
  summarise_at(c("d1", "d2", "d3"), sd)


full_data_m_1$age <- "1 month"
full_data_m_2$age <- "2 month"


full_data <- rbind(full_data_m_1, full_data_m_2)

file_list <- list.files(pattern="export_\\d+.csv")

period_data <- as_tibble(do.call(rbind, lapply(
  file_list, function(x) cbind(read.csv(x), 
                               period=strtoi(str_extract(x, "[0-9]+"))))))

file_list2 <- list.files(pattern="export_2month_\\d+.csv")

period_data2 <- as_tibble(
  do.call(rbind, lapply(
    file_list2, function(x) cbind(read.csv(x), 
                                  period=strtoi(str_extract(x, "(?<=month_)[0-9]+"))))))
period_data$period = period_data$period / 60/60
period_data2$period = period_data2$period / 60/60

file_list_e <- list.files(pattern="export_edges_\\d+.csv")

edges_by_period <- as_tibble(do.call(rbind, lapply(
  file_list_e, function(x) cbind(read.csv(x), 
                               period=strtoi(str_extract(x, "[0-9]+"))))))

file_list_e2 <- list.files(pattern="export_edges_twomonth_\\d+.csv")

edges_by_period2 <- as_tibble(do.call(rbind, lapply(
  file_list_e2, function(x) cbind(read.csv(x), 
                                 period=strtoi(str_extract(x, "[0-9]+"))))))

edge_img <- readPNG("central.png")

distances <- read.csv("full_distances.csv")

file_list_d <- list.files(pattern="export_distance_\\d+.csv")
dist_by_period <- as_tibble(do.call(rbind, lapply(
  file_list_d, function(x) cbind(read.csv(x), 
                                 period=strtoi(str_extract(x, "[0-9]+"))))))


# DISCRIMINATION INDEX FIGURE

d1 <- full_data %>% 
  arrange(age) %>% 
    ggplot(aes(x = as.factor(age), y = d1, fill = as.factor(age))) +
      geom_boxplot() +
  geom_hline(yintercept = 0, linetype = "dashed", color = "#661100") +
  stat_compare_means(comparisons = list(c("1 month", "2 month")), method = "t.test", dodge = 0.6) +
  scale_fill_manual(values =c(safe_colorblind_palette[1], safe_colorblind_palette[8])) +
  labs(title = "D1",
       y = "Discrimination index (D1)") +
  theme(axis.title.x = element_blank(),
        axis.ticks.x = element_blank(),
        legend.position = "none",
        legend.title = element_blank(),
        plot.title = element_text(hjust = 0.5))+
  annotation_custom(grobTree(textGrob("A", x=0.02,  y=0.95, hjust=0.0, gp=gpar(col="black", fontsize=10))))

  
d2 <- full_data %>% 
  arrange(age) %>% 
  ggplot(aes(x = as.factor(age), y = d2, fill = as.factor(age))) +
  geom_boxplot() +
  scale_fill_manual(values =c(safe_colorblind_palette[1], safe_colorblind_palette[8])) +
  geom_hline(yintercept = 0, linetype = "dashed", color = "#661100") +
  stat_compare_means(comparisons = list(c("1 month", "2 month")), method = "t.test", dodge = 0.6) +
  labs(title = "D2",
       y = "Discrimination index (D2)") +
  ylim(-1, 1) +
  theme(axis.title.x = element_blank(),
        axis.ticks.x = element_blank(),
        legend.position="none",
        legend.title = element_blank(),
        plot.title = element_text(hjust = 0.5))+
  annotation_custom(grobTree(textGrob("B", x=0.02,  y=0.95, hjust=0.0, gp=gpar(col="black", fontsize=10))))


d3 <- full_data %>% 
  arrange(age) %>% 
  ggplot(aes(x = as.factor(age), y = d3, fill = as.factor(age))) +
  geom_boxplot() +
  stat_compare_means(comparisons = list(c("1 month", "2 month")), method = "t.test", dodge = 0.6) +
  geom_hline(yintercept = 0.5, linetype = "dashed", color = "#661100") +
  scale_fill_manual(values =c(safe_colorblind_palette[1], safe_colorblind_palette[8])) +
  labs(title = "D3",
       y = "Discrimination index (D3)") +
  ylim(0, 1) +
  theme(axis.title.x = element_blank(),
        axis.ticks.x = element_blank(),
        legend.position="none",
        legend.title = element_blank(),
        plot.title = element_text(hjust = 0.5)) +
  annotation_custom(grobTree(textGrob("C", x=0.02,  y=0.95, hjust=0.0, gp=gpar(col="black", fontsize=10))))


d2_by_indv <- full_data %>% 
  arrange(age) %>% 
  ggplot(aes(x = reorder(X, d2), y = d2, fill = as.factor(age))) +
  geom_col() +
  geom_text(aes(label=round(d2, 2)), position=position_dodge(width=0.9), vjust=-0.25) +
  geom_hline(yintercept = 0, linetype = "dashed", color = "#661100") +
  scale_fill_manual(values =c(safe_colorblind_palette[1], safe_colorblind_palette[8])) +
  ylim(-1, 1) +
  theme(axis.title.x = element_blank(),
        axis.text.x = element_blank(),
        axis.ticks.x = element_blank(),
        plot.title = element_text(hjust = 0.5),
        legend.position = "bottom") +
  labs(y = "Discrimination index",
       fill = "Age",
       title = "D2 by individual fish") +
  annotation_custom(grobTree(textGrob("Preference for Novel Object", x=0.5,  y=0.95, hjust=0.5,
                                      gp=gpar(col=safe_colorblind_palette[4], fontsize=12)))) +
  annotation_custom(grobTree(textGrob("🠕", x=0.5,  y=0.78, hjust=0.5,
                                      gp=gpar(col=safe_colorblind_palette[4], fontsize=60)))) +
  annotation_custom(grobTree(textGrob("🠗", x=0.5,  y=0.22, hjust=0.5,
                                      gp=gpar(col=safe_colorblind_palette[10], fontsize=60)))) +
  annotation_custom(grobTree(textGrob("Preference for Familiar Object", x=0.5,  y=0.05, hjust=0.5,
                                      gp=gpar(col=safe_colorblind_palette[10], fontsize=12)))) +
  annotation_custom(grobTree(textGrob("D", x=0.02,  y=0.95, hjust=0.0, gp=gpar(col="black", fontsize=10))))

d2_by_time <- ggplot() +
  geom_smooth(aes(x = period, y = d2), data = period_data, fill = safe_colorblind_palette[1], color = safe_colorblind_palette[1]) +
  geom_smooth(aes(x = period, y = d2), data = period_data2, fill= safe_colorblind_palette[8], color = safe_colorblind_palette[8]) +
  ylim(-1, 1) +
  theme(plot.title = element_text(hjust = 0.5)) +
  coord_cartesian(xlim=c(0, 37)) +
  geom_hline(yintercept = 0, linetype = "dashed", color = "#661100") +
  labs(x = "Time (minutes)",
       y = "Discrimination index (D2)",
       title = "Change in D2 over time") +
  annotation_custom(grobTree(textGrob("E", x=0.02,  y=0.95, hjust=0.0, gp=gpar(col="black", fontsize=10))))

# 900x1200
grid.arrange(d1, d2, d3, d2_by_indv, d2_by_time, layout_matrix = rbind(c(1, 2, 3), c(4, 4, 4), c(5, 5, 5)))



# EXPLORATION TIME FIGURE

full_data$pc_xp_same <- full_data$e1 / full_data$num_frames_same * 100
full_data$pc_xp_diff <- full_data$e2 / full_data$num_frames_diff * 100
period_data$pc_xp_same <- period_data$e1 / period_data$num_frames_same * 100
period_data$pc_xp_diff <- period_data$e2 / period_data$num_frames_diff * 100
period_data2$pc_xp_same <- period_data2$e1 / period_data2$num_frames_same * 100
period_data2$pc_xp_diff <- period_data2$e2 / period_data2$num_frames_diff * 100


bxp_xpr <- full_data %>% 
  melt(id=c("X", "age")) %>% 
  filter(variable == "pc_xp_same" | variable == "pc_xp_diff") %>% 
  ggplot(aes(x = as.factor(age), y = value, fill = variable)) +
  geom_boxplot(position = position_dodge2(width=0.75)) +
  stat_compare_means(comparisons = list(c("1 month", "2 month")), label = "p.signif", method = "t.test", dodge = 0.6) +
  stat_compare_means(aes(group = variable), label = "p.signif", method = "t.test", dodge = 2) +
  theme(plot.title = element_text(hjust = 0.5),
        legend.title = element_blank(),
        legend.position = "bottom") +
  labs(y = "Frames spent exploring (%)",
       x = "Age",
       fill = "Test",
       title = "Exploration by age") +
  scale_fill_manual(labels = c("Training Phase", "Testing Phase"), values = c(safe_colorblind_palette[2], safe_colorblind_palette[4])) +
  annotation_custom(grobTree(textGrob("A", x=0.02,  y=0.95, hjust=0.0, gp=gpar(col="black", fontsize=10))))


lgr_xpr_one <- period_data %>% 
  group_by(period) %>% 
  as.data.frame() %>% 
  melt(id=c("X", "period")) %>% 
  filter(variable == "pc_xp_same" | variable == "pc_xp_diff") %>% 
  ggplot(aes(x = as.factor(period), y = value, group = variable, color = variable, fill = variable)) +
  geom_smooth() +  
  guides(fill= FALSE, color=guide_legend(override.aes=list(fill=NA))) +
  theme(plot.title = element_text(hjust = 0.5),
        legend.title = element_blank(),
        legend.position = "none") +
  labs(y = "Frames spent exploring (%)",
       x = "Time (Minutes)",
       fill = "Test",
       title = "Exploration: One Month") +
  scale_color_manual(labels = c("Training Phase", "Testing Phase"), values = c(safe_colorblind_palette[2], safe_colorblind_palette[4])) +
  scale_fill_manual(labels = c("Training Phase", "Testing Phase"), values = c(safe_colorblind_palette[2], safe_colorblind_palette[4])) +
  annotation_custom(grobTree(textGrob("B", x=0.02,  y=0.95, hjust=0.0, gp=gpar(col="black", fontsize=10))))


lgr_xpr_two <- period_data2 %>% 
  group_by(period) %>% 
  as.data.frame() %>% 
  melt(id=c("X", "period")) %>% 
  filter(variable == "pc_xp_same" | variable == "pc_xp_diff") %>% 
  ggplot(aes(x = as.factor(period), y = value, group = variable, fill = variable, color = variable)) +
  geom_smooth() +  
  guides(fill= FALSE, color=guide_legend(override.aes=list(fill=NA))) +
  theme(plot.title = element_text(hjust = 0.5),
        legend.title = element_blank(),
        legend.position = "bottom") +
  labs(y = "Frames spent exploring (%)",
       x = "Time (Minutes)",
       fill = "Test",
       color = "None",
       title = "Exploration: Two Month") +
  scale_color_manual(labels = c("Training Phase", "Testing Phase"), values = c(safe_colorblind_palette[2], safe_colorblind_palette[4])) +
  scale_fill_manual(labels = c("Training Phase", "Testing Phase"), values = c(safe_colorblind_palette[2], safe_colorblind_palette[4])) +
  annotation_custom(grobTree(textGrob("C", x=0.02,  y=0.95, hjust=0.0, gp=gpar(col="black", fontsize=10))))


grid.arrange(bxp_xpr, lgr_xpr_one, lgr_xpr_two, layout_matrix = cbind(c(1, 1, 1, 1), c(2, 2, 3, 3)))

# EDGE OF SCREEN ANALYSIS
edges_by_period$percentage = (edges_by_period$Frames.at.edge / edges_by_period$Total.Frames) * 100

onemonthe <- edges_by_period %>% 
  ggplot(aes(x = period/60/60, y = percentage, fill = Trial, color = Trial)) +
  geom_smooth() +
  guides(fill= FALSE, color=guide_legend(override.aes=list(fill=NA))) +
  theme(plot.title = element_text(hjust = 0.5),
        legend.title = element_blank(),
        legend.position = "bottom") +
  labs(y = "Edge Frames (%)",
       x = "Time (minutes)",
       fill = "Test",
       color = "None",
       title = "Frames at edge: 1 month") +
  ylim(0, 100) +
  scale_color_manual(labels = c("Testing Phase", "Training Phase"), values = c(safe_colorblind_palette[4], safe_colorblind_palette[2])) +
  scale_fill_manual(labels = c("Testing Phase", "Training Phase" ), values = c(safe_colorblind_palette[4], safe_colorblind_palette[2])) +
  annotation_custom(grobTree(textGrob("A", x=0.02,  y=0.95, hjust=0.0, gp=gpar(col="black", fontsize=10))))

edges_by_period2$percentage = (edges_by_period2$Frames.at.edge / edges_by_period2$Total.Frames) * 100

twomonthe <- edges_by_period2 %>% 
  ggplot(aes(x = period/60/60, y = percentage, fill = Trial, color = Trial)) +
  geom_smooth() +
  guides(fill= FALSE, color=guide_legend(override.aes=list(fill=NA))) +
  theme(plot.title = element_text(hjust = 0.5),
        legend.title = element_blank(),
        legend.position = "bottom") +
  labs(y = "Edge Frames (%)",
       x = "Time (minutes)",
       fill = "Test",
       color = "None",
       title = "Frames at edge: 2 month") +
  ylim(0, 100) +
  scale_color_manual(labels = c("Testing Phase", "Training Phase"), values = c(safe_colorblind_palette[4], safe_colorblind_palette[2])) +
  scale_fill_manual(labels = c("Testing Phase", "Training Phase" ), values = c(safe_colorblind_palette[4], safe_colorblind_palette[2])) +
  annotation_custom(grobTree(textGrob("B", x=0.02,  y=0.95, hjust=0.0, gp=gpar(col="black", fontsize=10))))

grid.arrange(onemonthe, twomonthe, rasterGrob(edge_img), layout_matrix = rbind(c(1, 2), c(3, 3)))

grid.arrange(onemonthe, twomonthe, rasterGob(edge_img), layout_matrix = rbind(c(1, 2), c(3, 3)))

# DISTANCE TRAVELLED

distances <- read.csv("distances_1m.csv")
distances$X = NULL

distances %>% 
  ggplot(aes(x = frame_id, y = distance, color = trial)) +
  geom_smooth()

distances %>% 
  order(distances$frame_id) %>% 
  

distances$trial <- factor(distances$trial, levels=c("same", "diff"))

distances %>%
  ggplot() +
  geom_boxplot(aes(x = trial, y = X0, fill = trial)) +
  labs(
    y = "Total distance travelled (pixel)",
    x = "Phase"
  ) +
  scale_fill_manual(labels = c("Training Phase", "Testing Phase"), values = c(safe_colorblind_palette[2], safe_colorblind_palette[4]))

dist_by_period[!rowSums(dist_by_period['period'] >= 144000),] %>% 
  ggplot(aes(x = period, y = distance, fill = Trial, color = Trial)) +
  geom_smooth() +
  theme(plot.title = element_text(hjust = 0.5),
        legend.title = element_blank(),
        legend.position = "bottom") +
  labs(x = "Time (frames)",
       y = "Distance travelled (pixel)",
      title = "Total distance travelled by 5 minute slice") +
  scale_color_manual(labels = c("Testing Phase", "Training Phase"), values = c(safe_colorblind_palette[4], safe_colorblind_palette[2])) +
  scale_fill_manual(labels = c("Testing Phase", "Training Phase" ), values = c(safe_colorblind_palette[4], safe_colorblind_palette[2]))

# SPEEDS

same_speeds <- read.csv("speeds_same_1m.csv", header = FALSE)
names(same_speeds) <- c("speed", "frame")
diff_speeds <- read.csv("speeds_diff_1m.csv", header = FALSE)
names(diff_speeds) <- c("speed", "frame")
same_speeds$trial <- 'Training Phase'
diff_speeds$trial <- 'Testing Phase'

full_speeds <- rbind(same_speeds, diff_speeds)

full_s_bxp_fill <- c("Training Phase" = safe_colorblind_palette[2],
                     "Testing Phase" = safe_colorblind_palette[4])


full_speed_line <- full_speeds %>% 
  ggplot() +
  geom_smooth(aes(x = frame/60/60, y = speed, color = fct_inorder(trial), fill = fct_inorder(trial))) +
  theme(plot.title = element_text(hjust = 0.5),
        legend.title = element_blank(),
        legend.position = "none") +
  labs(
    x = "Time (minutes)",
    y = "Velocity (pixels/s)",
    title = "Velocity of fish by frame (1 Month)"
  ) +
  scale_color_manual(labels = c("Training Phase", "Testing Phase"), values = c(safe_colorblind_palette[2], safe_colorblind_palette[4])) +
  scale_fill_manual(labels = c("Training Phase", "Testing Phase"), values = c(safe_colorblind_palette[2], safe_colorblind_palette[4])) +
annotation_custom(grobTree(textGrob("A", x=0.02,  y=0.95, hjust=0.0, gp=gpar(col="black", fontsize=10))))


same_obj_a_v <- read.csv("speeds_same_obj_a.csv", header = FALSE)
same_obj_b_v <- read.csv("speeds_same_obj_b.csv", header = FALSE)
diff_obj_a_v <- read.csv("speeds_diff_obj_a.csv", header = FALSE)
diff_obj_b_v <- read.csv("speeds_diff_obj_b.csv", header = FALSE)

same_obj_a_v$trial <- 'Training: Object A'
same_obj_b_v$trial <- 'Training: Object B'

diff_obj_a_v$trial <- 'Testing: Object A'
diff_obj_b_v$trial <- 'Testing: Object B'

full_speeds_by_obj <- rbind(same_obj_a_v, same_obj_b_v, diff_obj_a_v, diff_obj_b_v)
names(full_speeds_by_obj) <- c("speed", 'frame', 'trial')

full_speeds_by_obj %>% 
  ggplot() +
  geom_smooth(aes(x = frame, y = speed, color = trial, fill = trial))

multiobjectocmparison <- c("Training: Left Object" = safe_colorblind_palette[2],
                  "Training: Right Object" = safe_colorblind_palette[6], 
                  "Testing: Familiar Object" = safe_colorblind_palette[4],
                  "Testing: Novel Object" = safe_colorblind_palette[7])


obj_speeds <- full_speeds_by_obj %>% 
  ggplot(aes(x = fct_inorder(trial), y = speed)) + 
  geom_boxplot(outlier.shape = NA, fill = multiobjectocmparison) +
  coord_cartesian(ylim=c(0, 890)) +
  theme(axis.title.x = element_blank(),
        axis.ticks.x = element_blank(),
        plot.title = element_text(hjust = 0.5)) +
  labs(title = "Velocities close to objects (1 Month)",
       y = "Velocity (pixels/s)") +
  stat_compare_means(comparisons = list(c("Testing: Object A", "Testing: Object B")), label = "p.signif", method = "t.test", label.y = 650) +
stat_compare_means(comparisons = list(c("Training: Object A", "Training: Object B")), label = "p.signif",  method = "t.test", label.y = 650) +
annotation_custom(grobTree(textGrob("C", x=0.02,  y=0.95, hjust=0.0, gp=gpar(col="black", fontsize=10))))


full_speed_bxp <- full_speeds %>% 
  ggplot(aes(x = fct_inorder(trial), y = speed)) +
  geom_boxplot(outlier.shape = NA, fill = full_s_bxp_fill) +
  theme(plot.title = element_text(hjust = 0.5),
        legend.title = element_blank(),
        axis.title.x = element_blank()) +
  labs(
    y = "Velocity (pixels/s)",
    title = "Velocity of fish (1 Month)"
  ) +
  coord_cartesian(ylim = c(0, 800)) +
  stat_compare_means(comparisons = list(c("Training Phase", "Testing Phase")), label = "p.signif", method = "t.test", label.y = 650) +
annotation_custom(grobTree(textGrob("B", x=0.02,  y=0.95, hjust=0.0, gp=gpar(col="black", fontsize=10))))

# Now all over again for 2 month fish

same_speeds2 <- read.csv("speeds_same_2m.csv", header = FALSE)
names(same_speeds2) <- c("speed", "frame")
diff_speeds2 <- read.csv("speeds_diff_2m.csv", header = FALSE)
names(diff_speeds2) <- c("speed", "frame")
same_speeds2$trial <- 'Training Phase'
diff_speeds2$trial <- 'Testing Phase'

full_speeds2 <- rbind(same_speeds2, diff_speeds2)

full_s_bxp_fill <- c("Training Phase" = safe_colorblind_palette[2],
                     "Testing Phase" = safe_colorblind_palette[4])

full_speed_line2 <- full_speeds2 %>% 
  ggplot() +
  geom_smooth(aes(x = frame/60/60, y = speed, color = fct_inorder(trial), fill = fct_inorder(trial))) +
  theme(plot.title = element_text(hjust = 0.5),
        legend.title = element_blank(),
        legend.position = "bottom") +
  labs(
    x = "Time (minutes)",
    y = "Velocity (pixels/s)",
    title = "Velocity of fish by frame (2 Month)"
  ) +
  scale_color_manual(labels = c("Training Phase", "Testing Phase"), values = c(safe_colorblind_palette[2], safe_colorblind_palette[4])) +
  scale_fill_manual(labels = c("Training Phase", "Testing Phase"), values = c(safe_colorblind_palette[2], safe_colorblind_palette[4])) +
annotation_custom(grobTree(textGrob("D", x=0.02,  y=0.95, hjust=0.0, gp=gpar(col="black", fontsize=10))))

same_obj_a_v2 <- read.csv("speeds_same_obj_a2.csv", header = FALSE)
same_obj_b_v2 <- read.csv("speeds_same_obj_b2.csv", header = FALSE)
diff_obj_a_v2 <- read.csv("speeds_diff_obj_a2.csv", header = FALSE)
diff_obj_b_v2 <- read.csv("speeds_diff_obj_b2.csv", header = FALSE)

same_obj_a_v2$trial <- 'Training: Object A'
same_obj_b_v2$trial <- 'Training: Object B'

diff_obj_a_v2$trial <- 'Testing: Object A'
diff_obj_b_v2$trial <- 'Testing: Object B'

full_speeds_by_obj2 <- rbind(same_obj_a_v2, same_obj_b_v2, diff_obj_a_v2, diff_obj_b_v2)
names(full_speeds_by_obj2) <- c("speed", 'frame', 'trial')

full_speeds_by_obj2 %>% 
  ggplot() +
  geom_smooth(aes(x = frame, y = speed, color = trial, fill = trial))

multiobjectocmparison <- c("Training: Left Object" = safe_colorblind_palette[2],
                           "Training: Right Object" = safe_colorblind_palette[6], 
                           "Testing: Familiar Object" = safe_colorblind_palette[4],
                           "Testing: Novel Object" = safe_colorblind_palette[7])


obj_speeds2 <- full_speeds_by_obj2 %>% 
  ggplot(aes(x = fct_inorder(trial), y = speed)) + 
  geom_boxplot(outlier.shape = NA, fill = multiobjectocmparison) +
  coord_cartesian(ylim=c(0, 1000)) +
  theme(axis.title.x = element_blank(),
        axis.ticks.x = element_blank(),
        plot.title = element_text(hjust = 0.5)) +
  labs(title = "Velocities close to objects (2 Month)",
       y = "Velocity (pixels/s)") +
  stat_compare_means(comparisons = list(c("Testing: Object A", "Testing: Object B")), label = "p.signif", method = "t.test", label.y = 850) +
  stat_compare_means(comparisons = list(c("Training: Object A", "Training: Object B")), label = "p.signif",  method = "t.test", label.y = 850)+
annotation_custom(grobTree(textGrob("F", x=0.02,  y=0.95, hjust=0.0, gp=gpar(col="black", fontsize=10))))


full_speed_bxp2 <- full_speeds2 %>% 
  ggplot(aes(x = fct_inorder(trial), y = speed)) +
  geom_boxplot(outlier.shape = NA, fill = full_s_bxp_fill) +
  theme(plot.title = element_text(hjust = 0.5),
        legend.title = element_blank(),
        axis.title.x = element_blank()) +
  labs(
    y = "Velocity (pixels/s)",
    title = "Velocity of fish (2 Month)"
  ) +
  coord_cartesian(ylim = c(0, 1100)) +
  stat_compare_means(comparisons = list(c("Training Phase", "Testing Phase")), label = "p.signif", method = "t.test", label.y = 900) +
annotation_custom(grobTree(textGrob("E", x=0.02,  y=0.95, hjust=0.0, gp=gpar(col="black", fontsize=10))))



grid.arrange(full_speed_line, full_speed_bxp, obj_speeds, full_speed_line2, full_speed_bxp2, obj_speeds2, layout_matrix = rbind(cbind(c(1, 1), c(2, 3)), cbind(c(4, 4), c(5, 6))))

# ACCELERATIONS!

full_accs_1_m_s <- read.csv("acc_sds_same.csv")
full_accs_1_m_d <- read.csv("acc_sds_diff.csv")

full_accs_1_m_s$trial <- 'Training Phase'
full_accs_1_m_d$trial <- 'Testing Phase'

full_accs_1_m <- rbind(full_accs_1_m_s, full_accs_1_m_d)

accs_1m_line <- full_accs_1_m %>% 
  melt(id = c("X", 'trial')) %>% 
  ggplot(aes(x = X/60/60, y = value, color = fct_inorder(trial), fill = fct_inorder(trial))) +
  geom_smooth() +
  theme(
    plot.title = element_text(hjust = 0.5),
    legend.title = element_blank(),
    legend.position = "none") +
  labs(
    x = "Time (Minutes)",
    y = "SD of acceleration px/s²",
    title = "Erratic behaviour (1 Month)"
  ) +   
  scale_color_manual(labels = c("Training Phase", "Testing Phase"), values = c(safe_colorblind_palette[2], safe_colorblind_palette[4])) +
  scale_fill_manual(labels = c("Training Phase", "Testing Phase"), values = c(safe_colorblind_palette[2], safe_colorblind_palette[4])) +
annotation_custom(grobTree(textGrob("A", x=0.02,  y=0.95, hjust=0.0, gp=gpar(col="black", fontsize=10))))


accs_1m_bxp <- full_accs_1_m %>% 
  melt(id = c("X", 'trial')) %>% 
  ggplot(aes(x = fct_inorder(trial), y = value)) +
  geom_boxplot(outlier.shape = NA, fill = full_s_bxp_fill) +
  coord_cartesian(ylim = c(0, 5500)) +
  theme(      plot.title = element_text(hjust = 0.5),
axis.title.x = element_blank()) +
  labs(title = "Erratic Behaviour (1 Month)",
       y = "SD of acceleration px/s²") +
  stat_compare_means(comparisons = list(c("Training Phase", "Testing Phase")), label = "p.signif", method = "t.test", label.y = 4500) +
  annotation_custom(grobTree(textGrob("B", x=0.02,  y=0.95, hjust=0.0, gp=gpar(col="black", fontsize=10))))

full_accs_2_m_s <- read.csv("acc_sds_same2.csv")
full_accs_2_m_d <- read.csv("acc_sds_diff2.csv")

full_accs_2_m_s$trial <- 'Training Phase'
full_accs_2_m_d$trial <- 'Testing Phase'

full_accs_2_m <- rbind(full_accs_2_m_s, full_accs_2_m_d)
  
accs_2m_line <- full_accs_2_m %>% 
  melt(id = c("X", "trial")) %>% 
    ggplot(aes(x = X/60/60, y = value, color = fct_inorder(trial), fill = fct_inorder(trial))) +
    geom_smooth() +
    theme(
      plot.title = element_text(hjust = 0.5),
      legend.title = element_blank(),
      legend.position = "bottom"
    ) +
    labs(
      x = "Time (Minutes)",
      y = "SD of acceleration px/s²",
      title = "Erratic behaviour (2 Month)"
    ) +   
    scale_color_manual(labels = c("Training Phase", "Testing Phase"), values = c(safe_colorblind_palette[2], safe_colorblind_palette[4])) +
    scale_fill_manual(labels = c("Training Phase", "Testing Phase"), values = c(safe_colorblind_palette[2], safe_colorblind_palette[4])) +
    annotation_custom(grobTree(textGrob("C", x=0.02,  y=0.95, hjust=0.0, gp=gpar(col="black", fontsize=10))))
  
  
accs_2m_bxp <- full_accs_2_m %>% 
  melt(id = c("X", "trial")) %>% 
    ggplot(aes(x = fct_inorder(trial), y = value)) +
    geom_boxplot(outlier.shape = NA, fill = full_s_bxp_fill) +
    coord_cartesian(ylim = c(0, 5000)) +
  theme(axis.title.x = element_blank(),
        plot.title = element_text(hjust = 0.5)) +
  labs(
    y = "SD of acceleration px/s²",
    title = "Erratic behaviour (2 Month)"
  ) +   
    stat_compare_means(comparisons = list(c("Training Phase", "Testing Phase")), label = "p.signif", method = "t.test", label.y = 4200) +
  annotation_custom(grobTree(textGrob("D", x=0.02,  y=0.95, hjust=0.0, gp=gpar(col="black", fontsize=10))))

grid.arrange(accs_1m_line, accs_1m_bxp, accs_2m_line, accs_2m_bxp, layout_matrix = rbind(c(1, 2), c(3, 4)))

# Erraticness by dist

err_same_1m <- read.csv("err_same.csv")
err_diff_1m <- read.csv("err_diff.csv")

err_same_1m$trial <- 'Training'
err_diff_1m$trial <- 'Testing'

full_err_1m <- rbind(err_same_1m, err_diff_1m)
full_err_1m$X <- NULL


full_err_1m_mean <- as_tibble(aggregate(x=full_err_1m$erraticness,
                              by=list(full_err_1m$frame_id, full_err_1m$trial),
                              FUN = mean))

names(full_err_1m_mean) <- c('frame_id', 'trial', 'erraticness')

full_err_1m %>% 
  ggplot() +
  geom_histogram(aes(erraticness), bins =800)

ggplot() +
  geom_smooth(aes(x = frame_id/60/60, y = erraticness, color = fct_inorder(trial), fill = fct_inorder(trial)), data = full_err_1m[!rowSums(full_err_1m['frame_id'] > 144000),]) +
  labs(x = "Time (minutes)",
       y = "Efficency of movement",
       title = "Efficency of movement (1 Month)") +
  theme(plot.title = element_text(hjust = 0.5),
        legend.title = element_blank(),
        legend.position = "bottom") +
  scale_color_manual(labels = c("Training Phase", "Testing Phase"), values = c(safe_colorblind_palette[2], safe_colorblind_palette[4])) +
  scale_fill_manual(labels = c("Training Phase", "Testing Phase"), values = c(safe_colorblind_palette[2], safe_colorblind_palette[4])) +
  annotation_custom(grobTree(textGrob("A", x=0.02,  y=0.95, hjust=0.0, gp=gpar(col="black", fontsize=10))))

# Erraticness by bearing


full_brs_1_m_s <- read.csv("br_sds_same.csv")
full_brs_1_m_d <- read.csv("br_sds_diff.csv")

full_brs_1_m_s$trial <- 'Training Phase'
full_brs_1_m_d$trial <- 'Testing Phase'

full_brs_1_m <- rbind(full_brs_1_m_s, full_brs_1_m_d)
trim <- full_brs_1_m[!rowSums(full_brs_1_m['X'] >= 144000),]
trim %>% 
  as.data.table() %>% 
  melt(id = c("X", "trial")) %>% 
  ggplot(aes(x = X/60/60, y = value, color = fct_inorder(trial), fill = fct_inorder(trial))) +
  geom_smooth()


brs <- read.csv("bearing_change.csv")
brs$X <- NULL

brs[!rowSums(brs['frame_id'] >= 144000),] %>% 
  ggplot(aes(x = frame_id/60/60, y = angle_diff_deg, color = trial)) +
  geom_smooth()

brs %>% 
  ggplot() +
  geom_boxplot(aes(x = trial, y = angle_diff_deg), outlier.shape = NA) +
  coord_cartesian(ylim=c(0, 35))

# Full accelerations

same <- read.csv("accs_full_new.csv")
diff <- read.csv("accs_full_new_d.csv")
ggplot() +
  geom_line(aes(X, mean, color="Training"), data=same, alpha=0.3) +
  geom_smooth(aes(X, mean, color = "Training"), data = same) +
  geom_line(aes(X, mean, color="Testing"), data=diff, alpha=0.3) +
  geom_smooth(aes(X, mean, color="Testing"), data = diff) +
  labs(x = "Frame ID",
       y = "Mean standard deviation",
       color = "Legend") +
  scale_color_manual(values = colours_full_accs)



same_obj_acc <- read.csv("same_fish_rolling_sd.csv")
diff_obj_acc <- read.csv("diff_fish_rolling_sd.csv")

colours_full_accs <- c("Training" = safe_colorblind_palette[4],
                       "Testing" = safe_colorblind_palette[2])

ggplot() +
  geom_line(aes(X, mean, color="Training"), data=same_obj_acc, alpha=0.3) +
  geom_smooth(aes(X, mean, color = "Training"), data = same_obj_acc) +
  geom_line(aes(X, mean, color="Testing"), data=diff_obj_acc, alpha=0.3) +
  geom_smooth(aes(X, mean, color="Testing"), data = diff_obj_acc) +
  labs(x = "Frame ID",
       y = "Mean standard deviation",
       color = "Legend") +
  scale_color_manual(values = colours_full_accs)





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
  geom_smooth(aes(x = V2, y = V1, color = "Training: Left Object"), data=same_obj_a, size = 1.0) +
  geom_smooth(aes(x = V2, y = V1, color = "Training: Right Object"), data=same_obj_b, size = 1.0) +
  geom_smooth(aes(x = V2, y = V1, color = "Testing: Familiar Object"), data=diff_obj_a, size = 1.0) +
  geom_smooth(aes(x = V2, y = V1, color = "Testing: Novel Object"), data=diff_obj_b, size = 1.0) +
  ggtitle("Accelerations near objects", ) +
  labs(x = "Time (frames)",
       y = "Acceleration (pixels/s^2)",
       color = "Legend") +
  scale_color_manual(values = colours_accs)


# ADD FRAME IDS TOO AND PLOT GEOM SMOOTH

ggplot() +
  geom_density(aes(V1, color = "Training: Left Object", fill = "Training: Left Object")
               , data=same_obj_a, alpha = 0.4, lwd = 0.8, adjust = 0.5)+
  geom_density(aes(V1, color = "Training: Right Object", fill = "Training: Right Object")
               , data=same_obj_b, alpha = 0.4, lwd = 0.8, adjust = 0.5) +
    geom_density(aes(V1, color = "Testing: Familiar Object", fill = "Testing: Familiar Object")
                , data=diff_obj_a, alpha = 0.4, lwd = 0.8, adjust = 0.5) +
    geom_density(aes(V1, color = "Testing: Novel Object", fill = "Testing: Novel Object")
                 , data=diff_obj_b, alpha = 0.4, lwd = 0.8, adjust = 0.5)
  
# FREEZING

frz_s_1 <- read.csv("freeze_same_1m.csv", header = FALSE)
frz_d_1 <- read.csv("freeze_diff_1m.csv", header = FALSE)

ggplot() +
  geom_freqpoly(aes(x = V1), data = frz_s_1, bins = 15, color = "blue") +
  geom_freqpoly


ggplot() +
  geom_line(aes(x = V1, y = cumsum(V1)), data = frz_s_1)