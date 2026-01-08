#! /usr/bin/ruby
#encoding: utf-8
#Nutrition browser 2020 import 0.2.0 (2025/01/07)

#==============================================================================
#STATIC
#==============================================================================
@debug = false


#==============================================================================
#LIBRARY
#==============================================================================
require './nb2020-soul'

#==============================================================================
#DEFINITION
#==============================================================================

def set_query_num( query, values, items, skips, nums )
	q = query
	items.each.with_index do |e, i|
		unless skips.include?( e )
			if nums.include?( e )
				q << " #{e}='#{values[i].to_i}',"
			else
				q << " #{e}='#{values[i]}',"
			end
		end
	end
	
	return q.chop!
end

def set_query_str( query, values, items, skips, strs )
	q = query
	items.each.with_index do |e, i|
		unless skips.include?( e )
			unless strs.include?( e )
				q << " #{e}='#{values[i].to_i}',"
			else
				q << " #{e}='#{values[i]}',"
			end
		end
	end
	
	return q.chop!
end

#==============================================================================
# Main
#==============================================================================

#### data loading
import_solid = []
items = []
txt_class = ''
line1_flag = true
line2_flag = false

opt = ARGV[0]
data_file = ARGV[1]
if ARGV[1] == nil
	data_file = opt 
	opt = 'ad'
end

if data_file == nil
	puts 'Nutrition browser 2020 import 0.0.0 (2024/10/14)'
	puts '[Usage]ruby nb2020-import.rb mode_option data'
	puts '[Mode option]'
	puts 'xx -> exchange'
	puts 'ow -> overwrite'
	puts 'ad -> add (default)'
	exit
end


File.open( data_file, 'r' ) do |f|
	f.each_line do |line|
		if line1_flag
			a = line.chomp.split( "\s" )
			if a[0] == 'NB2020' && /^\[\w+\]$/ =~ a[1]
				txt_class = a[1].sub( '[', '' ).sub( ']', '' )
				line1_flag = false
				line2_flag = true
			else
				puts 'Incomplete data.'
				exit( 0 )
			end
		elsif line2_flag
			items = line.chomp.split( "\t" )
			line2_flag = false
		else
			import_solid << line.force_encoding( 'utf-8' ).chomp.split( "\t" )
		end
	end
end
puts "[#{txt_class}]#{opt}"
puts items

if import_solid.size == 0
	puts 'Empty data.'
	exit
end

#### DB upadate
count = 0
case txt_class
when 'dic'
	#FG org_name alias user def_fn
	if import_solid[0].size == 5
		$DB.query( "DELETE FROM #{$TB_DIC};" ) if opt == 'xx'

		import_solid.each do |e|
			print "#{count}\r"

			begin
				res = $DB.query( "SELECT * FROM #{$TB_DIC} WHERE FG='#{e[0]}' AND org_name='#{e[1]}' AND alias='#{e[2]}';" )

				if res.first
					if opt == 'ow'
						$DB.query( "UPDATE #{$TB_DIC} SET user='#{e[3]}', def_fn='#{e[4]}' WHERE FG='#{e[0]}'AND org_name='#{e[1]}' AND alias='#{e[2]}';" )
					else
						puts "[SKIP]#{e}"
					end
				else

					$DB.query( "INSERT INTO #{$TB_DIC} SET FG='#{e[0]}', org_name='#{e[1]}', alias='#{e[2]}', user='#{e[3]}', def_fn='#{e[4]}';" )
				end

			rescue
				puts "[ERROR]#{e}"
			end
			count += 1
		end
	else
		puts 'Incomplete dic data.'
	end
	puts "#{count} data have imported."

when 'fctp'
	# user, @fct_item
	if true #items.size == 14
		$DB.query( "DELETE FROM #{$TB_FCTP};" ) if opt == 'xx'
 
 		nums = %w( REFUSE ENERC ENERC_KCAL )
		import_solid.each do |e|
			values = Array.new( 100 )
			values = e.dup

			print "#{count}\r"
			begin
				res = $DB.query( "SELECT * FROM #{$TB_FCTP} WHERE user='#{values[0]}' AND FN='#{values[2]}';" )
				if res.first
					if opt == 'ow'
						query = "UPDATE #{$TB_FCTP} SET"
						skips = %w( user FN SID )
						query = set_query_num( query, values, items, skips, nums )
						query<< " WHERE user='#{values[0]}' AND FN='#{values[2]}';"

						$DB.query( query )
					else
						puts "[SKIP]#{values}"
					end
				else
					query = "INSERT INTO #{$TB_FCTP} SET"
					skips = %w( SID )
					query = set_query_num( query, values, items, skips, nums )
					query<< ";"

					$DB.query( query ) unless values[2].to_s.empty?
				end
			rescue
				puts "[ERROR]#{e}"
			end
			count += 1
		end
	else
		puts 'Incomplete fctp data.'
	end
	puts "#{count} data have imported."

when 'tagp'
	# FG, FN, SID, SN, user, name, class1, class2, class3, tag1, tag2, tag3, tag4, tag5, status
	if items.size == 15
#		$DB.query( "DELETE FROM #{$TB_TAG};" ) if opt == 'xx'
 		nums = %w( SN status )

		import_solid.each do |e|
			values = Array.new( 20 )
			values = e.dup

			print "#{count}\r"
			begin
				res = $DB.query( "SELECT * FROM #{$TB_TAG} WHERE FN='#{values[1]}' AND user='#{values[4]}';" )
				if res.first
					if opt == 'ow'
						query = "UPDATE #{$TB_TAG} SET"
						skips = %w( FN user )
						query = set_query_num( query, values, items, skips, strs )
						query << " WHERE FN='#{values[1]}' AND user='#{values[4]}';"

						$DB.query( query )
					else
						puts "[SKIP]#{values}"
					end
				else
					query = "INSERT INTO #{$TB_TAG} SET"
					skips = %w( dummy )
					query = set_query_num( query, values, items, skips, strs )
					query << ";"

					$DB.query( query ) unless values[1].to_s.empty? || values[4].to_s.empty?
				end
			rescue
				puts "[ERROR]#{e}"
			end
			count += 1
		end
	else
		puts 'Incomplete tagp data.'
	end
	puts "#{count} data have imported."

when 'extp'
	# FN, user, gycv, allergen1, allergen2, unit, color1, color2, color1h, color2h, shun1s, shun1e, shun2s, shun2e
	if items.size == 14
#		$DB.query( "DELETE FROM #{$TB_EXT};" ) if opt == 'xx'
 		strs = %w( unit )

		import_solid.each do |e|
			values = Array.new( 20 )
			values = e.dup

			print "#{count}\r"
			begin
				res = $DB.query( "SELECT * FROM #{$TB_EXT} WHERE FN='#{values[0]}' AND user='#{values[1]}';" )
				if res.first
					if opt == 'ow'
						query = "UPDATE #{$TB_EXT} SET"
						skips = %w( FN user )
						query = set_query_str( query, values, items, skips, strs )
						query << " WHERE FN='#{values[0]}' AND user='#{values[1]}';"

						$DB.query( query )
					else
						puts "[SKIP]#{values}"
					end
				else
					query = "INSERT INTO #{$TB_TAG} SET"
					skips = %w( dummy )
					query = set_query_str( query, values, items, skips, strs )
					query << ";"

					$DB.query( query ) unless values[0].to_s.empty? || values[1].to_s.empty?
				end
			rescue
				puts "[ERROR]#{e}"
			end
			count += 1
		end
	else
		puts 'Incomplete extp data.'
	end
	puts "#{count} data have imported."

when 'recipe'
	# code, user, root, branch, public, protect, draft, favorite, name, dish, type, role, tech, time, cost, sum, protocol, date

	if items.size == 14
#		$DB.query( "DELETE FROM #{$TB_EXT};" ) if opt == 'xx'
 		strs = %w( code user root name protocol sum date )

		import_solid.each do |e|
			values = Array.new( 20 )
			values = e.dup

			print "#{count}\r"
			begin
				res = $DB.query( "SELECT * FROM #{$TB_RECIPE} WHERE code='#{values[0]}' AND user='#{values[1]}';" )
				if res.first
					if opt == 'ow'
						query = "UPDATE #{$TB_EXT} SET"
						skips = %w( code user protocol )
						query = set_query_str( query, values, items, skips, strs )

						plotocol = values[16].gsub( '<n>', "\n"  )
						query << ", protocol='#{plotocol}' WHERE FN='#{values[0]}' AND user='#{values[1]}';"

#						$DB.query( query )
					else
						puts "[SKIP]#{values}"
					end
				else
					query = "INSERT INTO #{$TB_RECIPE} SET"
					skips = %w( protocol )
					query = set_query_str( query, values, items, skips, strs )

					plotocol = values[16].gsub( '<n>', "\n"  )
					query << ", protocol='#{plotocol}';"

#					$DB.query( query ) unless values[0].to_s.empty? || values[1].to_s.empty?
				end
			rescue
				puts "[ERROR]#{e}"
			end
			count += 1
		end
	else
		puts 'Incomplete extp data.'
	end
	puts "#{count} data have imported."

else
	puts 'Importable data list..'
	puts 'dic'
	puts 'ftcp'
	puts 'tagp'
	puts 'extp'
end

