library(tidyverse)
library(lubridate)
library(humaniformat)

raw <- read_csv("aha-dissertations.csv")

schools <- raw |>
  select(aha_school_id, school) |>
  distinct() |>
  arrange(aha_school_id) |>
  mutate(school = str_replace_all(school, "Univ.", "University"),
         school = str_replace_all(school, "Coll.", "College"),
         school = str_replace_all(school, "Can.", "Canada"),
         school = str_replace_all(school, "Inst.", "Institute")) |>
  filter(school != "State University of New York, Stony Brook",
         school != "State University of New York, Buffalo",
         school != "State University of New York, Albany",
         school != "ianUniversity of Illinois, Urbana-Champaign") |>
  mutate(school = str_trim(school)) |>
  mutate(id = row_number()) |>
  select(id, aha_school_id, school)

write_csv(schools, "schools.csv")

replace_na <- function(x) {
  if_else(is.na(x), "", x)
}

dissertators <- raw |> select(aha_dissertator_id, name_first, name_middle, name_last, name_suffix) |>
  mutate(first = replace_na(name_first),
         middle = replace_na(name_middle),
         last = replace_na(name_last),
         suffix = replace_na(name_suffix)) |>
  mutate(name = str_c(first, middle, last, suffix, sep = " "),
         name = name |> str_replace_all("\\s+", " ") |> str_trim()) |>
  select(aha_scholar_id = aha_dissertator_id, name, name_first, name_middle, name_last, name_suffix) |>
  arrange(aha_scholar_id)

cm1 <- raw |> select(aha_dissertation_id, aha_scholar_id = advisor_id, name = advisor) |>
  mutate(role = "chair") |>
  mutate(name = str_trim(name)) |>
  filter(!is.na(name))

cm2 <- raw |> select(aha_dissertation_id, aha_scholar_id = advisor_2_id, name = Advisord_2) |>
  mutate(role = "reader") |>
  mutate(name = str_trim(name)) |>
  filter(!is.na(name))

committee_members <- bind_rows(cm1, cm2) |>
  mutate(name_first = name |> first_name(),
         name_middle = name |> middle_name(),
         name_last = name |> last_name(),
         name_suffix = name |> suffix())

scholars <- bind_rows(dissertators, committee_members |> select(-aha_dissertation_id, -role)) |>
  distinct(aha_scholar_id, .keep_all = TRUE) |>
  arrange(aha_scholar_id) |>
  mutate(id = row_number()) |>
  select(id, aha_scholar_id, name, starts_with("name_")) |>
  mutate(orcid = NA_character_)

write_csv(scholars, "scholars.csv")

dissertations <- raw |>
  arrange(aha_dissertation_id) |>
  mutate(id = row_number()) |>
  select(id, aha_dissertation_id, title, aha_author_id = aha_dissertator_id, date, aha_school_id) |>
  mutate(year = date |> mdy() |> year()) |>
  mutate(title = str_trim(title)) |>
  select(-date) |>
  left_join(scholars |> select(author_id = id, aha_author_id = aha_scholar_id), by = "aha_author_id") |>
  left_join(schools |> select(school_id = id, aha_school_id), by = "aha_school_id") |>
  select(id, aha_dissertation_id, title, year, author_id, aha_author_id, school_id, aha_school_id)

write_csv(dissertations, "dissertations.csv")

committee_members <- committee_members |>
  left_join(dissertations |> select(dissertation_id = id, aha_dissertation_id), by = "aha_dissertation_id") |>
  left_join(scholars |> select(scholar_id = id, aha_scholar_id), by = "aha_scholar_id") |>
  select(dissertation_id, aha_dissertation_id, scholar_id, aha_scholar_id, role) |>
  arrange(dissertation_id)

write_csv(committee_members, "committee-members.csv")

