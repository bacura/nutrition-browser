#! /usr/bin/ruby
#encoding: utf-8
#Nutrition browser 2020 memory linker 0.00b

#==============================================================================
#CHANGE LOG
#==============================================================================
#20210425	0.00b	start


#==============================================================================
#LIBRARY
#==============================================================================
require 'mysql2'


#==============================================================================
#STATIC
#==============================================================================
$MYSQL_HOST = 'localhost'
$MYSQL_USER = 'user'
$MYSQL_PW = 'password'
$MYSQL_DB = 'nb2020'
$MYSQL_TB_MEMORY = 'memory'
db = Mysql2::Client.new(:host => "#{$MYSQL_HOST}", :username => "#{$MYSQL_USER}", :password => "#{$MYSQL_PW}", :database => "#{$MYSQL_DB}", :encoding => "utf8" )

@debug = false


#==============================================================================
#DEFINITION
#==============================================================================


#==============================================================================
# Main
#==============================================================================

category_list = []
pointer_list = []
memory = []

#### Lording all pointer
puts "Lording all pointer.\n"
r = db.query( "SELECT * FROM #{$MYSQL_TB_MEMORY};" )
r.each do |e|
	pointer_list << e['pointer']
	category_list << e['category']
end


#### Adding pointer mark
puts "Adding pointer mark.\n"
r.each do |e|
	memory = e['content']

	pointer_sub_list = []
	pointer_list.each do |ee| pointer_sub_list << memory.scan( ee ) end
	pointer_sub_list.flatten!
	pointer_sub_list.uniq!
	pointer_sub_list_ = Array.new( pointer_sub_list )

	# Removing smaller pointer & number
	pointer_sub_list.size.times do |c|
		pointer_sub_list_.each do |e|
			begin
				pointer_sub_list[c] = nil if /#{pointer_sub_list[c]}/ =~ e && pointer_sub_list[c] != e || /\d+/ =~ e || e.size < 2
			rescue
				pointer_sub_list[c] = nil
				puts "ERROR.\n"
			end
		end
	end

	pointer_sub_list.each do |ee|
		memory.gsub!( ee, "{{#{ee}}}" ) if ee != nil && ee != e['pointer']
	end
	memory.gsub!( '{{{{', '{{' )
	memory.gsub!( '}}}}', '}}' )
	db.query( "UPDATE #{$MYSQL_TB_MEMORY} SET content='#{memory}' WHERE category='#{e['category']}' AND pointer='#{e['pointer']}';" )
end

#### Evaluating Rank
#puts "Counting.\n"
#each_count = []

#r.each do |e| each_count << ( e['know'].to_f / e['count'].to_f ) end

#puts "Evaluating total rank.\n"
#total_rank = each_count.map { |v| each_count.count { |a| a > v } + 1 }

#c = 0
#r.each do |e|
#	trank = 11 - ( total_rank[c].to_f / total_rank.size * 10 ).ceil
#	db.query( "UPDATE #{$MYSQL_TB_MEMORY} SET total_rank='#{trank}' WHERE category='#{e['category']}' AND pointer='#{e['pointer']}';" )
#	c += 1
#end

#puts "Evaluating category rank.\n"
#category_list.each do |e|
#	rr = db.query( "SELECT * FROM #{$MYSQL_TB_MEMORY} WHERE category='#{e}';" )
#
#	each_count = []
#	rr.each do |e| each_count << ( e['know'].to_f / e['count'].to_f ) end

#	puts "#{e} rank.\n"
#	category_rank = each_count.map { |v| each_count.count { |a| a > v } + 1 }

#	c = 0
#	rr.each do |ee|
#		rank = 11 - ( category_rank[c].to_f / category_rank.size * 10 ).ceil
#		db.query( "UPDATE #{$MYSQL_TB_MEMORY} SET rank='#{rank}' WHERE category='#{ee['category']}' AND pointer='#{ee['pointer']}';" )
#		c += 1
#	end
#end

puts "Done.\n"
