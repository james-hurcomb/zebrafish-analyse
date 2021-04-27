setwd("~/Documents/zebrafish-analyse/stats_scripts")
library(tidyverse)
library(grid)
library(gtable)    
library(gridExtra)
library(reshape)
require(png)
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

file_list_e <- list.files(pattern="export_edges_\\d+.csv")

edges_by_period <- as_tibble(do.call(rbind, lapply(
  file_list_e, function(x) cbind(read.csv(x), 
                               period=strtoi(str_extract(x, "[0-9]+"))))))

file_list_e2 <- list.files(pattern="export_edges_twomonth_\\d+.csv")

edges_by_period2 <- as_tibble(do.call(rbind, lapply(
  file_list_e2, function(x) cbind(read.csv(x), 
                                 period=strtoi(str_extract(x, "[0-9]+"))))))

edge_img <- readPNG("central.png")

# DISCRIMINATION INDEX FIGURE

d1 <- full_data %>% 
  arrange(age) %>% 
    ggplot() +
      geom_boxplot(aes(x = as.factor(age), y = d1, fill = as.factor(age))) +
  scale_fill_manual(values =c(safe_colorblind_palette[1], safe_colorblind_palette[8])) +
  labs(title = "D1") +
  theme(axis.title.x = element_blank(),
        axis.text.x = element_blank(),
        axis.ticks.x = element_blank(),
        legend.position = "none",
        legend.title = element_blank(),
        axis.title.y = element_blank(),
        plot.title = element_text(hjust = 0.5))+
  annotation_custom(grobTree(textGrob("A", x=0.02,  y=0.95, hjust=0.0, gp=gpar(col="black", fontsize=10))))

  
d2 <- full_data %>% 
  arrange(age) %>% 
  ggplot() +
  geom_boxplot(aes(x = as.factor(age), y = d2, fill = as.factor(age))) +
  scale_fill_manual(values =c(safe_colorblind_palette[1], safe_colorblind_palette[8])) +
  labs(title = "D2") +
  ylim(-1, 1) +
  theme(axis.title.x = element_blank(),
        axis.text.x = element_blank(),
        axis.ticks.x = element_blank(),
        legend.position="none",
        legend.title = element_blank(),
        axis.title.y = element_blank(),
        plot.title = element_text(hjust = 0.5))+
  annotation_custom(grobTree(textGrob("B", x=0.02,  y=0.95, hjust=0.0, gp=gpar(col="black", fontsize=10))))


d3 <- full_data %>% 
  arrange(age) %>% 
  ggplot() +
  geom_boxplot(aes(x = as.factor(age), y = d3, fill = as.factor(age))) +
  scale_fill_manual(values =c(safe_colorblind_palette[1], safe_colorblind_palette[8])) +
  labs(title = "D3") +
  ylim(0, 1) +
  theme(axis.title.x = element_blank(),
        axis.text.x = element_blank(),
        axis.ticks.x = element_blank(),
        legend.position="none",
        legend.title = element_blank(),
        axis.title.y = element_blank(),
        plot.title = element_text(hjust = 0.5)) +
  annotation_custom(grobTree(textGrob("C", x=0.02,  y=0.95, hjust=0.0, gp=gpar(col="black", fontsize=10))))


d2_by_indv <- full_data %>% 
  arrange(age) %>% 
  ggplot(aes(x = reorder(X, d2), y = d2, fill = as.factor(age))) +
  geom_col() +
  geom_text(aes(label=round(d2, 2)), position=position_dodge(width=0.9), vjust=-0.25) +
  scale_fill_manual(values =c(safe_colorblind_palette[1], safe_colorblind_palette[8])) +
  ylim(-1, 1) +
  theme(axis.title.x = element_blank(),
        axis.text.x = element_blank(),
        axis.ticks.x = element_blank(),
        plot.title = element_text(hjust = 0.5)) +
  labs(y = "Discrimination index",
       fill = "Age",
       title = "D2 by individual fish") +
  annotation_custom(grobTree(textGrob("Preference for Novel Object", x=0.5,  y=0.95, hjust=0.5,
                                      gp=gpar(col=safe_colorblind_palette[4], fontsize=12)))) +
  annotation_custom(grobTree(textGrob("🠕", x=0.5,  y=0.83, hjust=0.5,
                                      gp=gpar(col=safe_colorblind_palette[4], fontsize=60)))) +
  annotation_custom(grobTree(textGrob("🠗", x=0.5,  y=0.17, hjust=0.5,
                                      gp=gpar(col=safe_colorblind_palette[10], fontsize=60)))) +
  annotation_custom(grobTree(textGrob("Preference for Familiar Object", x=0.5,  y=0.05, hjust=0.5,
                                      gp=gpar(col=safe_colorblind_palette[10], fontsize=12)))) +
  annotation_custom(grobTree(textGrob("D", x=0.02,  y=0.95, hjust=0.0, gp=gpar(col="black", fontsize=10))))


grid.arrange(d1, d2, d3, d2_by_indv, layout_matrix = rbind(c(1, 2, 3), c(1, 2, 3), c(4, 4, 4), c(4, 4, 4), c(4, 4, 4)))


# EXPLORATION TIME FIGURE

bxp_xpr <- full_data %>% 
  melt(id=c("X", "age")) %>% 
  filter(variable == "e1" | variable == "e2") %>% 
  ggplot() +
  geom_boxplot(aes(x = as.factor(age), y = value, fill = variable)) +
  theme(plot.title = element_text(hjust = 0.5),
        legend.title = element_blank(),
        legend.position = "bottom") +
  labs(y = "Frames spent exploring",
       x = "Age",
       fill = "Test",
       title = "Exploration by age") +
  scale_fill_manual(labels = c("Training Phase", "Testing Phase"), values = c(safe_colorblind_palette[2], safe_colorblind_palette[4])) +
  annotation_custom(grobTree(textGrob("A", x=0.02,  y=0.95, hjust=0.0, gp=gpar(col="black", fontsize=10))))


lgr_xpr_one <- period_data[!rowSums(period_data['period'] == 144000),] %>% 
  group_by(period) %>% 
  as.data.frame() %>% 
  melt(id=c("X", "period")) %>% 
  filter(variable == "e1" | variable == "e2") %>% 
  ggplot(aes(x = as.factor(period), y = value, group = variable, color = variable, fill = variable)) +
  geom_smooth() +  
  guides(fill= FALSE, color=guide_legend(override.aes=list(fill=NA))) +
  theme(plot.title = element_text(hjust = 0.5),
        legend.title = element_blank(),
        legend.position = "bottom") +
  labs(y = "Frames spent exploring",
       x = "Timeslice",
       fill = "Test",
       title = "Exploration: One Month") +
  scale_color_manual(labels = c("Training Phase", "Testing Phase"), values = c(safe_colorblind_palette[2], safe_colorblind_palette[4])) +
  scale_fill_manual(labels = c("Training Phase", "Testing Phase"), values = c(safe_colorblind_palette[2], safe_colorblind_palette[4])) +
  annotation_custom(grobTree(textGrob("B", x=0.02,  y=0.95, hjust=0.0, gp=gpar(col="black", fontsize=10))))


lgr_xpr_two <- period_data2[!rowSums(period_data2['period'] >= 144000),] %>% 
  group_by(period) %>% 
  as.data.frame() %>% 
  melt(id=c("X", "period")) %>% 
  filter(variable == "e1" | variable == "e2") %>% 
  ggplot(aes(x = as.factor(period), y = value, group = variable, fill = variable, color = variable)) +
  geom_smooth() +  
  guides(fill= FALSE, color=guide_legend(override.aes=list(fill=NA))) +
  theme(plot.title = element_text(hjust = 0.5),
        legend.title = element_blank(),
        legend.position = "bottom") +
  labs(y = "Frames spent exploring",
       x = "Timeslice",
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
  ggplot(aes(x = period, y = percentage, fill = Trial, color = Trial)) +
  geom_smooth() +
  guides(fill= FALSE, color=guide_legend(override.aes=list(fill=NA))) +
  theme(plot.title = element_text(hjust = 0.5),
        legend.title = element_blank(),
        legend.position = "bottom") +
  labs(y = "Frames spent at edge (%)",
       x = "Time (frames)",
       fill = "Test",
       color = "None",
       title = "Frames at edge: 1 month") +
  ylim(0, 100) +
  scale_color_manual(labels = c("Testing Phase", "Training Phase"), values = c(safe_colorblind_palette[4], safe_colorblind_palette[2])) +
  scale_fill_manual(labels = c("Testing Phase", "Training Phase" ), values = c(safe_colorblind_palette[4], safe_colorblind_palette[2])) +
  annotation_custom(grobTree(textGrob("A", x=0.02,  y=0.95, hjust=0.0, gp=gpar(col="black", fontsize=10))))

edges_by_period2$percentage = (edges_by_period2$Frames.at.edge / edges_by_period2$Total.Frames) * 100

twomonthe <- edges_by_period2 %>% 
  ggplot(aes(x = period, y = percentage, fill = Trial, color = Trial)) +
  geom_smooth() +
  guides(fill= FALSE, color=guide_legend(override.aes=list(fill=NA))) +
  theme(plot.title = element_text(hjust = 0.5),
        legend.title = element_blank(),
        legend.position = "bottom") +
  labs(y = "Frames spent at edge (%)",
       x = "Time (frames)",
       fill = "Test",
       color = "None",
       title = "Frames at edge: 2 month") +
  ylim(0, 100) +
  scale_color_manual(labels = c("Testing Phase", "Training Phase"), values = c(safe_colorblind_palette[4], safe_colorblind_palette[2])) +
  scale_fill_manual(labels = c("Testing Phase", "Training Phase" ), values = c(safe_colorblind_palette[4], safe_colorblind_palette[2])) +
  annotation_custom(grobTree(textGrob("B", x=0.02,  y=0.95, hjust=0.0, gp=gpar(col="black", fontsize=10))))

grid.arrange(onemonthe, twomonthe, rasterGrob(edge_img), layout_matrix = rbind(c(1, 2), c(3, 3)))

# Full accelerations

same_obj_acc <- read.csv("same_fish_rolling_sd.csv")
diff_obj_acc <- read.csv("diff_fish_rolling_sd.csv")

colours_full_accs <- c("Training" = safe_colorblind_palette[1],
                       "Testing" = safe_colorblind_palette[3])

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
  
# No

