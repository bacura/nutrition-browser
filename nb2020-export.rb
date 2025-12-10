#! /usr/bin/ruby
#encoding: utf-8
#Nutrition browser 2020 export 0.0.2 (2024/10/14)

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

case ARGV[0]
when 'unit'
	export = ''
	puts "SELECT * FROM #{$MYSQL_TB_EXT};"
	r = $DB.query( "SELECT * FROM #{$MYSQL_TB_EXT};" )
	r.each do |e| export << "#{e['FN']}\t#{e['unit']}\n" end
	puts "NB2020 [unit] data #{@date}\n"
	puts export.force_encoding( 'UTF-8' )

when 'gycv'
	export = ''
	r = $DB.query( "SELECT * FROM #{$MYSQL_TB_EXT} WHERE gycv=1;" )
	r.each do |e| export << "#{e['FN']}\n" end
	puts "NB2020 [gycv] data #{@date}\n"
	puts export.force_encoding( 'UTF-8' )

when 'shun'
	export = ''
	r = $DB.query( "SELECT * FROM #{$MYSQL_TB_EXT};" )
	r.each do |e| export << "#{e['FN']}\t#{e['shun1s']}\t#{e['shun1e']}\t#{e['shun2s']}\t#{e['shun2e']}\n" end
	puts "NB2020 [shun] data\n"
	puts export.force_encoding( 'UTF-8' )

when 'allergen'
	export = ''
	r = $DB.query( "SELECT * FROM #{$MYSQL_TB_EXT};" )
	r.each do |e| export << "#{e['FN']}\t#{e['allergen1']}\t#{e['allergen2']}\n" end
	puts "NB2020 [allergen] data #{@date}\n"
	puts export.force_encoding( 'UTF-8' )

when 'dic'
	export = ''
	r = $DB.query( "SELECT * FROM #{$MYSQL_TB_DIC} ORDER BY FG, org_name;" )
	r.each do |e|
		export << "#{e['FG']}\t#{e['org_name']}\t#{e['alias'].gsub( '<br>', ',' )}\t#{e['user']}\t#{e['def_fn']}\n" unless e['org_name'].empty?
	end
	puts "NB2020 [dic] data #{@date}\n"
	puts export.force_encoding( 'UTF-8' )

when 'memory'
	export = ''
	r = $DB.query( "SELECT * FROM #{$MYSQL_TB_MEMORY};" )
	r.each do |e| export << "#{e['user']}\t#{e['category']}\t#{e['pointer']}\t#{e['memory']}\t#{e['rank']}\t#{e['total_rank']}\t#{e['count']}t#{e['know']}\t#{e['date']}\n" end
	puts "NB2020 [memory] data #{@date}\n"
	puts export.force_encoding( 'UTF-8' )
else
	puts 'Nutrition browser 2020 export 0.0.2 (2024/10/14)'
	puts '[Usage]ruby nb2020-export.rb Exportable data > nb2020-dic.txt'
	puts 'Exportable data list..'
	puts 'unit'
	puts 'gycv'
	puts 'shun'
	puts 'allergen'
	puts 'dic'
	puts 'memory'
end
