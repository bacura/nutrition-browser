#! /usr/bin/ruby
#encoding: utf-8
#Nutrition browser 2020 import 0.2.1 (2025/01/10)

#==============================================================================
#STATIC
#==============================================================================
@debug = false


#==============================================================================
#LIBRARY
#==============================================================================
require './nb2020-soul'
require 'date'

#==============================================================================
#DEFINITION
#==============================================================================

def set_query( query, values, items, skips )
	q = query
	items.each.with_index do |e, i|
		q << " #{e}='#{values[i]}'," unless skips.include?( e )
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
				count += 1
			rescue
				puts "[ERROR]#{e}"
			end
		end
	else
		puts 'Incomplete dic data.'
	end
	puts "#{count} data have imported."

when 'fctp'
	tb = $TB_FCTP
	# user, @fct_item
	if true #items.size == 14
		$DB.query( "DELETE FROM #{tb};" ) if opt == 'xx'
 
		import_solid.each do |e|
			values = Array.new( 100 )
			values = e.dup

			print "#{count}\r"
			begin
				res = $DB.query( "SELECT * FROM #{tb} WHERE user='#{values[0]}' AND FN='#{values[2]}';" )
				if res.first
					if opt == 'ow'
						query = "UPDATE #{tb} SET"
						skips = %w( user FN SID )
						query = set_query( query, values, items, skips )
						query<< " WHERE user='#{values[0]}' AND FN='#{values[2]}';"

						$DB.query( query )
					else
						puts "[SKIP]#{values}"
					end
				else
					query = "INSERT INTO #{tb} SET"
					skips = %w( SID )
					query = set_query( query, values, items, skips )
					query<< ";"

					$DB.query( query ) unless values[2].to_s.empty?
				end
				count += 1
			rescue
				puts "[ERROR]#{e}"
			end
		end
	else
		puts "Incomplete #{tb} data."
	end
	puts "#{count} data have imported."

when 'tagp'
	tb = $TB_TAG
	# FG, FN, SID, SN, user, name, class1, class2, class3, tag1, tag2, tag3, tag4, tag5, status
	if items.size == 15
#		$DB.query( "DELETE FROM #{tb};" ) if opt == 'xx'

		import_solid.each do |e|
			values = Array.new( 100 )
			values = e.dup

			print "#{count}\r"
			begin
				res = $DB.query( "SELECT * FROM #{tb} WHERE FN='#{values[1]}' AND user='#{values[4]}';" )
				if res.first
					if opt == 'ow'
						query = "UPDATE #{tb} SET"
						skips = %w( FN SN user )
						query = set_query( query, values, items, skips )
						query << " WHERE FN='#{values[1]}' AND user='#{values[4]}';"

						$DB.query( query )
					else
						puts "[SKIP]#{values}"
					end
				else
					query = "INSERT INTO #{tb} SET"
					skips = %w( SN )
					query = set_query( query, values, items, skips )
					query << ";"

					$DB.query( query ) unless values[1].to_s.empty? || values[4].to_s.empty?
				end
				count += 1
			rescue
				puts "[ERROR]#{e}"
			end
		end
	else
		puts "Incomplete #{tb} data."
	end
	puts "#{count} data have imported."

when 'extp'
	tb = $TB_EXT
	# FN, user, gycv, allergen1, allergen2, unit, color1, color2, color1h, color2h, shun1s, shun1e, shun2s, shun2e
	if items.size == 14
#		$DB.query( "DELETE FROM #{tb};" ) if opt == 'xx'

		import_solid.each do |e|
			values = Array.new( 100 )
			values = e.dup

			print "#{count}\r"
			begin
				res = $DB.query( "SELECT * FROM #{tb} WHERE FN='#{values[0]}' AND user='#{values[1]}';" )
				if res.first
					if opt == 'ow'
						query = "UPDATE #{tb} SET"
						skips = %w( FN user )
						query = set_query( query, values, items, skips )
						query << " WHERE FN='#{values[0]}' AND user='#{values[1]}';"

						$DB.query( query )
					else
						puts "[SKIP]#{values}"
					end
				else
					query = "INSERT INTO #{tb} SET"
					skips = %w( dummy )
					query = set_query( query, values, items, skips )
					query << ";"

					$DB.query( query ) unless values[0].to_s.empty? || values[1].to_s.empty?
				end
				count += 1
			rescue
				puts "[ERROR]#{e}"
			end
		end
	else
		puts "Incomplete #{tb} data."
	end
	puts "#{count} data have imported."

when 'recipe'
	# code, user, root, branch, public, protect, draft, favorite, name, dish, type, role, tech, time, cost, sum, protocol, date
	tb = $TB_RECIPE

	if items.size == 18
		$DB.query( "DELETE FROM #{tb};" ) if opt == 'xx'

		import_solid.each do |e|
			values = Array.new( 100 )
			values = e.dup

			print "#{count}\r"
			begin
				res = $DB.query( "SELECT * FROM #{tb} WHERE code='#{values[0]}' AND user='#{values[1]}';" )
				if res.first
					if opt == 'ow'
						query = "UPDATE #{tb} SET"
						skips = %w( code user sum protocol )
						query = set_query( query, values, items, skips )

						sum = values[15].gsub( '<t>', "\t"  )
						plotocol = values[16].gsub( '<n>', "\n"  )

						query << ", sum='#{sum}', protocol='#{plotocol}' WHERE code='#{values[0]}' AND user='#{values[1]}';"

						$DB.query( query )
					else
						puts "[SKIP]#{values}"
					end
				else
					query = "INSERT INTO #{tb} SET"
					skips = %w( sum protocol )
					query = set_query( query, values, items, skips )
					sum = values[15].gsub( '<t>', "\t"  )
					plotocol = values[16].gsub( '<n>', "\n"  )
					query << ", sum='#{sum}', protocol='#{plotocol}';"

					$DB.query( query ) unless values[0].to_s.empty? || values[1].to_s.empty?
				end
				count += 1

			rescue
				puts "[ERROR]#{e}"
			end
		end
	else
		puts "Incomplete #{tb} data."
	end
	puts "#{count} data have imported."

when 'media'
	# user, code, origin, base, type, date, zidx, alt, secure
	tb = $TB_MEDIA

	if items.size == 9
		$DB.query( "DELETE FROM #{tb};" ) if opt == 'xx'

		import_solid.each do |e|
			values = Array.new( 100 )
			values = e.dup

			print "#{count}\r"
			begin
				res = $DB.query( "SELECT * FROM #{tb} WHERE user='#{values[0]}' AND code='#{values[1]}';" )
				if res.first
					if opt == 'ow'
						query = "UPDATE #{tb} SET"
						skips = %w( code user alt )
						query = set_query( query, values, items, skips )
						alt = values[8].gsub( '<n>', "\n"  )
						query << ", alt='#{alt}' WHERE user='#{values[0]}' AND code='#{values[1]}';"

						$DB.query( query )
					else
						puts "[SKIP]#{values}"
					end
				else
					query = "INSERT INTO #{tb} SET"
					skips = %w( alt )
					query = set_query( query, values, items, skips )
					alt = values[8].gsub( '<n>', "\n"  )
					query << ", alt='#{alt}';"

					$DB.query( query ) unless values[0].to_s.empty? || values[1].to_s.empty?
				end
				count += 1

			rescue
				puts "[ERROR]#{e}"
			end
		end
	else
		puts "Incomplete #{tb} data."
	end
	puts "#{count} data have imported."

else
	puts 'Importable data list..'
	puts 'dic'
	puts 'ftcp'
	puts 'tagp'
	puts 'extp'
	puts 'recipe'
	puts 'media'
end

