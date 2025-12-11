#! /usr/bin/ruby
# encoding: utf-8
# Nutrition browser 2020 cutting board monitor 0.0.4.AI ( 2024/08/17 )

#==============================================================================
# STATIC
#==============================================================================
@debug = false

#==============================================================================
# LIBRARY
#==============================================================================
require './soul'
require './brain'

#==============================================================================
# METHODS
#==============================================================================
def load_sum_for_user( db )
	r = db.query( "SELECT sum FROM #{$MYSQL_TB_SUM} WHERE user = '#{db.user.name}';", false )
	r.first['sum'].split( "\t" )
end

def update_sum( db, new_sum )
	db.query( "UPDATE #{$MYSQL_TB_SUM} SET sum = '#{new_sum}' WHERE user = '#{db.user.name}';", true )
end

def generate_new_sum( cb_num, r, food_no, food_weight, food_check )
	if cb_num.zero?
		"#{food_no}:#{food_weight}:g:#{food_weight}:#{food_check}::1.0:#{food_weight}"
	else
		sum_ = r.first['sum']
		"#{sum_}\t#{food_no}:#{food_weight}:g:#{food_weight}:#{food_check}::1.0:#{food_weight}"
	end
end

def process_change_mode( sum, base_fn, food_no, food_weight )
	new_sum = sum.map do |x|
		t = x.split( ':' )
		t[0] == base_fn ? "#{food_no}:#{food_weight}:g:#{food_weight}:#{t[4]}:#{t[5]}:1.0:#{food_weight}" : x
	end.join( "\t" )
	new_sum
end

#==============================================================================
# MAIN
#==============================================================================
html_init( nil )

user = User.new( @cgi )
user.debug if @debug
db = Db.new( user, @debug, false )

### User check
if user.name.nil?
	puts '-'
	exit
end


# POST parameters
food_no = @cgi['food_no']
food_weight = BigDecimal( food_weight_check( @cgi['food_weight'] ).first )
food_check = @cgi['food_check']
base_fn = @cgi['base_fn']
mode = @cgi['mode']


sum = load_sum_for_user( db )
cb_num = sum.size
new_sum = ''

case mode
when 'add'
	r = db.query( "SELECT sum FROM #{$MYSQL_TB_SUM} WHERE user = '#{user.name}';", false )
	new_sum = generate_new_sum( cb_num, r, food_no, food_weight, food_check )
	update_sum( db, new_sum )
	cb_num += 1

	# Updating history
	add_his( user, food_no )

when 'change'
	new_sum = process_change_mode( sum, base_fn, food_no, food_weight )
	update_sum( db, new_sum )

when 'refresh'
end

puts cb_num
