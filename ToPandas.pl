#-----------------------------------------------------------
sub ErrorState {
my ($v)=@_;
if ( $v eq 'OK') {
  return($v);
} else {
  return('KO');
}
}

#-----------------------------------------------------------
sub StartTime {
my ($v)=@_;
#$v=~s/\s+/-/;
return($v);
}

#-----------------------------------------------------------
sub Agent {
my ($v)=@_;
my @t=split(/\@/,$v);
my @t1=split(/:/,$t[1]);
return($t1[0]);
}

#-----------------------------------------------------------
sub ResponseTime {
my ($v)=@_;
$v=~s/,/./;
return($v);
}

#-----------------------------------------------------------
sub processFile {
while (my $l=<F>) {
  chomp($l);
  $l=~s/;jsessionid/#jsessionid/g;
  my @t=split(/;/,$l);
  my $str;
  foreach my $f (@KEEP) {
    if ( exists($FUNC{$f}) ) {
      $str.=$FUNC{$f}($t[$HFIELDS{$f}]);
    } else {
      $str.=$t[$HFIELDS{$f}];
    }
    $str.=";";
  }
  if ( $str ne '') {
    chop($str);
    print("$str\n");
  }
}
}

#-----------------------------------------------------------
sub processHeader {
my $l=<F>;
chomp($l);
$l=~s/\s+//g;
$l=~s/\[ms\]//g;
#print("$l\n");
print(join(";",@KEEP)."\n");

%HFIELDS;
@AFIELDS=split(/;/,$l);
for(my $i=0;$i<@AFIELDS;$i++) {
  $HFIELDS{$AFIELDS[$i]}=$i;
}

}

#-----------------------------------------------------------
$f=$ARGV[0];
open F,$f or die "Plouf";

@KEEP=qw(ErrorState PurePath ResponseTime Agent Application StartTime);
&processHeader();

%FUNC;
$FUNC{ErrorState}=\&ErrorState;
$FUNC{StartTime}=\&StartTime;
$FUNC{Agent}=\&Agent;
$FUNC{ResponseTime}=\&ResponseTime;

&processFile();
