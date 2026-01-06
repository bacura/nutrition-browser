#! /usr/bin/ruby
#encoding: utf-8
#Nutrition browser 2020 import 0.1.0 (2024/10/14)

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
puts "[#{txt_class}]"
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
 
		import_solid.each do |e|
			a = Array.new( 100 )
			a = e.dup

			print "#{count}\r"
			begin
				res = $DB.query( "SELECT * FROM #{$TB_FCTP} WHERE user='#{a[0]}' AND FN='#{a[2]}';" )
				if res.first
					if opt == 'ow'
						query = "UPDATE #{$TB_FCTP} SET"
						items.each.with_index do |e, i|
							query << " #{e}='#{a[i]}'," unless e == 'SID' || i == 1 || i == 4
						end
						query.chop!
						query<< " WHERE user='#{a[0]}' AND FN='#{a[2]}';"
						$DB.query( query )
					else
						puts "[SKIP]#{a}"
					end
				else
					query = "INSERT INTO #{$TB_FCTP} SET"
					items.each.with_index do |e, i|
						query << " #{e}='#{a[i]}'," unless e == 'SID'
					end
					query.chop!
					query<< ";"

					$DB.query( query ) unless a[2].to_s.empty?
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
	# FG, FN, SID, SN, user, name, class1, class2, class3, tag1, tag2, tag3, tag4, tag5
	if items.size == 14
		$DB.query( "DELETE FROM #{$TB_TAG};" ) if opt == 'xx'

		import_solid.each do |e|
			a = Array.new( 20 )
			a = e.dup

			print "#{count}\r"
			begin
				res = $DB.query( "SELECT * FROM #{$TB_TAG} WHERE FN='#{a[1]}' AND user='#{a[4]}';" )
				if res.first
					if opt == 'ow'
						$DB.query( "UPDATE #{$TB_TAG} SET FG='#{a[0]}', SID='#{a[2]}', SN='0', name='#{a[5]}', class1='#{a[6]}', class2='#{a[7]}', class3='#{a[8]}', tag1='#{a[9]}', tag2='#{a[10]}', tag3='#{a[11]}', tag4='#{a[12]}', tag5='#{a[13]}' WHERE FN='#{a[1]}'AND user='#{a[4]}';" )
					else
						puts "[SKIP]#{a}"
					end
				else
					$DB.query( "INSERT INTO #{$TB_TAG} SET FG='#{a[0]}', FN='#{a[1]}', SID='#{a[2]}', SN='0', user='#{a[4]}', name='#{a[5]}', class1='#{a[6]}', class2='#{a[7]}', class3='#{a[8]}', tag1='#{a[9]}', tag2='#{a[10]}', tag3='#{a[11]}', tag4='#{a[12]}', tag5='#{a[13]}';" ) unless a[1].to_s.empty?
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
		$DB.query( "DELETE FROM #{$TB_EXT};" ) if opt == 'xx'

		import_solid.each do |e|
			a = Array.new( 20 )
			a = e.dup

			print "#{count}\r"
			begin
				res = $DB.query( "SELECT * FROM #{$TB_EXT} WHERE FN='#{a[0]}' AND user='#{a[1]}';" )
				if res.first
					if opt == 'ow'
						$DB.query( "UPDATE #{$TB_EXT} SET gycv='#{a[2].to_i}', allergen1='#{a[3].to_i}', allergen2='#{a[4].to_i}', unit='#{a[5]}', color1=0, color2=0, color1h=0, color2h=0, shun1s='#{a[10].to_i}', shun1e='#{a[11].to_i}', shun2s='#{a[12].to_i}', shun2e='#{a[13].to_i}' WHERE FN='#{a[0]}'AND user='#{a[1]}';" )
					else
						puts "[SKIP]#{a}"
					end
				else
					$DB.query( "INSERT INTO #{$TB_EXT} SET FN='#{a[0]}', user='#{a[1]}', gycv='#{a[2].to_i}', allergen1='#{a[3].to_i}', allergen2='#{a[4].to_i}', unit='#{a[5]}', color1=0, color2=0, color1h=0, color2h=0, shun1s='#{a[10].to_i}', shun1e='#{a[11].to_i}', shun2s='#{a[12].to_i}', shun2e='#{a[13].to_i}';" ) unless a[0].to_s.empty?
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

