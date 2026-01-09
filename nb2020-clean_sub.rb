#! /usr/bin/ruby
#nb2020-clean_sub.rb for modified20230428

#Bacura KYOTO Lab
#Saga Ukyo-ku Kyoto, JAPAN
#https://bacura.jp
#yossy@bacura.jp


#==============================================================================
#DEFINITION
#==============================================================================
def cleaner( category, source_file, out_file )

	puts category
	data_solid = []

	#### First pass
	f = open( source_file, 'r' )
	f.each_line do |e|
		items = e.force_encoding( 'UTF-8' ).split( "\t" )

		#### common
		t = e.force_encoding( 'UTF-8' )
		t.sub!( 'AMMON-E', 'AMMONE' )
		t.sub!( 'FIB-SDFS', 'FIBSDFS' )
		t.sub!( 'FIB-SDFP', 'FIBSDFP' )
		t.sub!( 'FIB-IDF', 'FIBIDF' )
		t.sub!( 'FIB-TDF', 'FIBTDF' )

		data_solid << t unless t == "\n"
	end
	f.close


	#### Second pass
	header = data_solid.shift
	data_solid_ = []
	c = 0
	data_solid.each do |e|
		t = e.sub( /\t+\n/, "\n" )
		t.gsub!( '"', '' )
		a = t.split( "\t" )
		if /^\d\d/ =~ e && a.size >= 5
			data_solid_[c] = t
		else
			c -= 1
			data_solid_[c].chomp!
			data_solid_[c] << "<br>#{t}"
		end
		c += 1
	end
	data_solid_.unshift( header )

	# 成分表データの書き込み
	f = open( out_file, 'w' )
	data_solid_.each do |e| f.puts e end
	f.close
end

#==============================================================================
# MAIN
#==============================================================================

category = "Amino Acid"
source_file = '20230428-mxt_kagsei-mext_00001_AA.txt'
out_file = '20230428-mxt_kagsei-mext_00001_AA_clean.txt'
cleaner( category, source_file, out_file )

category = "Fatty Acid"
source_file = '20230428-mxt_kagsei-mext_00001_FA.txt'
out_file = '20230428-mxt_kagsei-mext_00001_FA_clean.txt'
cleaner( category, source_file, out_file )

category = "Fiber"
source_file = '20230428-mxt_kagsei-mext_00001_FIB.txt'
out_file = '20230428-mxt_kagsei-mext_00001_FIB_clean.txt'
cleaner( category,source_file, out_file )

category = "Suger"
source_file = '20230428-mxt_kagsei-mext_00001_SUG.txt'
out_file = '20230428-mxt_kagsei-mext_00001_SUG_clean.txt'
cleaner( category, source_file, out_file )

category = "Organic Acid"
source_file = '20230428-mxt_kagsei-mext_00001_OA.txt'
out_file = '20230428-mxt_kagsei-mext_00001_OA_clean.txt'
cleaner( category, source_file, out_file )
