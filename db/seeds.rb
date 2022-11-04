# This file should contain all the record creation needed to seed the database with its default values.
# The data can then be loaded with the bin/rails db:seed command (or created alongside the database with db:setup).
#
# Examples:
#
#   movies = Movie.create([{ name: "Star Wars" }, { name: "Lord of the Rings" }])
#   Character.create(name: "Luke", movie: movies.first)

require 'csv'

schools = []
CSV.foreach("db/aha-data/schools.csv", headers: true) do |row|
	schools << School.new(row.to_hash)
end
School.import schools

AdminUser.create!(email: ENV.fetch("DISSDB_ADMIN_USER"), 
									password: ENV.fetch("DISSDB_ADMIN_PASS"),
									password_confirmation: ENV.fetch("DISSDB_ADMIN_PASS")) if Rails.env.development?
