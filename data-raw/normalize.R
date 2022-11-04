library(tidyverse)
library(lubridate)

raw <- read_csv("raw.csv")

schools <- raw |>
  select(school_id, school) |>
  distinct() |>
  arrange(school_id) |>
  mutate(school = str_replace_all(school, "Univ.", "University"),
         school = str_replace_all(school, "Coll.", "College"),
         school = str_replace_all(school, "Can.", "Canada"),
         school = str_replace_all(school, "Inst.", "Institute")) |>
  rename(id = school_id, name = school)

write_csv(schools, "schools.csv")

replace_na <- function(x) {
  if_else(is.na(x), "", x)
}

fix_year <- function(x) {
  digits <- str_extract(x, "\\d+$")
  base <- as.integer(digits)
  year <- NA_integer_
  if (0 <= base & base <= 22) {
    year <- base + 2000
  } else if (base >= 1800) {
    year <- base
  } else {
    year <- base + 1900
  }
  return(year)
}
fix_years <- Vectorize(fix_year)

dissertators <- raw |>
  select(scholar_id, name_first = first, name_middle = middle, name_last = last, name_suffix = suffix) |>
  mutate(first = replace_na(name_first),
         middle = replace_na(name_middle),
         last = replace_na(name_last),
         suffix = replace_na(name_suffix)) |>
  mutate(name = str_c(first, middle, last, suffix, sep = " "),
         name = name |> str_replace_all("\\s+", " ") |> str_trim()) |>
  mutate(join_name = str_c(first, last, sep = " "),
         join_name = join_name |> str_replace_all("\\s+", " ") |> str_trim()) |>
  select(id = scholar_id, name, join_name, name_first, name_middle, name_last, name_suffix)

an1 <- dissertators |> count(name) |> filter(n > 1) |> pull(name)
an2 <- dissertators |> count(join_name) |> filter(n > 1) |> pull(join_name)
ambiguous_names <- c(an1, an2) |> unique() |> sort()

dissertators <- dissertators |>
  mutate(join_name = if_else(name %in% ambiguous_names | join_name %in% ambiguous_names,
                             NA_character_, join_name))

dissertators |>
  select(-join_name) |>
  write_csv("scholars.csv")

dissertations <- raw |>
  select(id = dissertation_id, title, scholar_id, school_id, title, date) |>
  mutate(year = fix_years(date)) |>
  mutate(title = str_trim(title)) |>
  select(-date)

write_csv(dissertations, "dissertations.csv")

cm1 <- raw |> select(dissertation_id, person = advisor) |>
  mutate(role = "chair") |>
  mutate(person = str_trim(person)) |>
  filter(!is.na(person))

cm2 <- raw |> select(dissertation_id, person = reader) |>
  mutate(role = "reader") |>
  mutate(person = str_trim(person)) |>
  filter(!is.na(person))

all_members <- bind_rows(cm1, cm2) |>
  left_join(dissertators, by = c("person" = "join_name"))

committee_members <- all_members |>
  rename(scholar_id = id) |>
  mutate(id = row_number()) |>
  select(id, dissertation_id, scholar_id, role, recorded_name = person)

write_csv(committee_members, "committee-members.csv")

