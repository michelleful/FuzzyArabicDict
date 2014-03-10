################################################################################
# AraMorph.pl  
# Portions (c) 2002 QAMUS LLC (www.qamus.org), 
# (c) 2002 Trustees of the University of Pennsylvania 
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation version 2.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details (../gpl.txt).
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
# 
# You can contact LDC by sending electronic mail to: ldc@ldc.upenn.edu
# or by writing to:
#                Linguistic Data Consortium
#                3600 Market Street
#                Suite 810
#                Philadelphia, PA, 19104-2653, USA.
################################################################################
# usage: 
# perl -w AraMorph.pl < infile > outfile
# were "infile" is the input text in Arabic Windows encoding (cp1256) 
# and "outfile" is the output text with morphology analyses and POS tags
# Not found items and related stats are written to STDERR and filename "notFound"

# load 3 compatibility tables (load these first so when we load the lexicons we can check for undeclared $cat values)
%hash_AB = load_table("tableAB"); # load compatibility table for prefixes-stems    (AB)
%hash_AC = load_table("tableAC"); # load compatibility table for prefixes-suffixes (AC)
%hash_BC = load_table("tableBC"); # load compatibility table for stems-suffixes    (BC)

# load 3 lexicons
%prefix_hash = load_dict("dictPrefixes"); # dict of prefixes (A)
%stem_hash   = load_dict("dictStems");    # dict of stems    (B)
%suffix_hash = load_dict("dictSuffixes"); # dict of suffixes (C)

while (<STDIN>) {

   #$file .= $_; # we might want to get stats on the orthography and fix it (eg. if there is no "Y" convert all "y" to "Y")
   print STDERR "reading input line $.\r";
   @tokens = tokenize($_); # returns a list of tokens (one line at a time)

   foreach $token (@tokens) {
      if ($token =~ m/[\x81\x8D\x8E\x90\xC1-\xD6\xD8-\xDB\xDD-\xDF\xE1\xE3-\xE6\xEC-\xED\xF0-\xF3\xF5\xF6\xF8\xFA]/) {
         # it's an Arabic word because it has 1 or more Ar. chars
         print "\nINPUT STRING: $token\n"; 
         $lookup_word = get_lookup($token); # returns the Arabic string without vowels/diacritics and converted to transliteration
         print "LOOK-UP WORD: $lookup_word\n"; $tokens++; $types{$lookup_word}++;

         if ( exists($found{$lookup_word}) ) {
            print $found{$lookup_word}; # no need to re-analyse it 
         }
         elsif ( exists($notfound{$lookup_word}) ) { # we keep %found and %notfound separate because %notfound can have additional lookups
            print $notfound{$lookup_word}; $freqnotfound{$lookup_word}++; 
         }
         else {
            if ( @solutions = analyze($lookup_word) ) { # if lookup word has 1 or more solutions
               foreach $solution (@solutions) {
                  $found{$lookup_word} .= $solution;
               }
               print $found{$lookup_word}; 
            }
            else {
               $notfound{$lookup_word} = "     Comment: $lookup_word NOT FOUND\n"; 

               if ( @alternatives = get_alternatives($lookup_word) ) { 
                  foreach $alt (@alternatives) {
                     $notfound{$lookup_word} .= " ALTERNATIVE: $alt\n";
                     if ( exists($found{$alt}) ) {
                        $notfound{$lookup_word} .= $found{$alt};
                     }
                     else {
                        if ( @solutions = analyze($alt) ) { 
                           foreach $solution (@solutions) {
                              $notfound{$lookup_word} .= $solution;
                           }
                        }
                        else {
                           $notfound{$lookup_word} .= "     Comment: $alt NOT FOUND\n";
                        }
                     }
                  }# end foreach
               }# end if
               print $notfound{$lookup_word}; $freqnotfound{$lookup_word}++;
            }
         }#end else
      }
      else {
        # it's not an Arabic word
        @nonArabictokens = tokenize_nonArabic($token); # tokenize it on white space
        foreach $item (@nonArabictokens) {
           print "\nINPUT STRING: $item\n     Comment: Non-Alphabetic Data\n" unless ($item eq " " or $item eq "");
        }
      }
   }#end foreach

}#end while

# ====================================================
# print out not-found words by frequency:
open (OUT, ">notFound") || die "cannot open: $!";
print STDERR "\n\n========= Some stats ============================\n";
@types = keys %types; $types = @types;
print STDERR "Tokens: $tokens -- Types: $types\n";
print STDERR "\n========= Frequency count of Not-Found =========\n";
my @items = keys %freqnotfound;
foreach my $item (sort { $freqnotfound{$b} <=> $freqnotfound{$a} } @items) {
   $rank++;
   print STDERR "$item\t$freqnotfound{$item}\n" unless ( $rank > 25 );
   print OUT "$item\t$freqnotfound{$item}\n"; # unless ( $rank > 25 );
}
close OUT;

# ============================
sub analyze { # returns a list of 1 or more solutions

   $this_word = shift @_; @solutions = (); $cnt = 0;
   segmentword($this_word); # get a list of valid segmentations
   foreach $segmentation (@segmented) {
      ($prefix,$stem,$suffix) = split ("\t",$segmentation); #print $segmentation, "\n";
      if (exists($prefix_hash{$prefix})) {
         if (exists($stem_hash{$stem})) {
            if (exists($suffix_hash{$suffix})) {
               # all 3 components exist in their respective lexicons, but are they compatible? (check the $cat pairs)
               foreach $prefix_value (@{$prefix_hash{$prefix}}) {
                  ($prefix, $voc_a, $cat_a, $gloss_a, $pos_a) = split (/\t/, $prefix_value);
                  foreach $stem_value (@{$stem_hash{$stem}}) {
                     #($stem, $voc_b, $cat_b, $gloss_b, $pos_b) = split (/\t/, $stem_value);
                     ($stem, $voc_b, $cat_b, $gloss_b, $pos_b, $lemmaID) = split (/\t/, $stem_value);
                     if ( exists($hash_AB{"$cat_a"." "."$cat_b"}) ) {
                        foreach $suffix_value (@{$suffix_hash{$suffix}}) {
                           ($suffix, $voc_c, $cat_c, $gloss_c, $pos_c) = split (/\t/, $suffix_value);
                           if ( exists($hash_AC{"$cat_a"." "."$cat_c"}) ) {
                              if ( exists($hash_BC{"$cat_b"." "."$cat_c"}) ) {
                                 #$cnt++; push (@solutions, "  SOLUTION $cnt: ($voc_a$voc_b$voc_c) $pos_a$pos_b$pos_c\n     (GLOSS): $gloss_a + $gloss_b + $gloss_c\n");
                                 $cnt++; push (@solutions, "  SOLUTION $cnt: ($voc_a$voc_b$voc_c) [$lemmaID] $pos_a$pos_b$pos_c\n     (GLOSS): $gloss_a + $gloss_b + $gloss_c\n");
                              }
                           }
                        }
                     }
                  }
               }# end foreach $prefix_value
            }
         }# end if (exists($stem_hash{$stem}))
      }
   }# end foreach $segmentation
   return (@solutions);

}

# ============================
sub get_alternatives { # returns a list of alternative spellings

   $word = shift @_; @alternatives = ();
   $temp = $word;

   if ($temp =~ m/Y'$/) {             # Y_w'_Y'
      $temp =~ s/Y/y/g;               # y_w'_y'
      push (@alternatives, $temp);    # y_w'_y'  -- pushed
      if ($temp =~ s/w'/&/) {         # y_&__y'
         push (@alternatives, $temp); # y_&__y'  -- pushed
      }
      $temp = $word;                  # Y_w'_Y'
      $temp =~ s/Y/y/g;               # y_w'_y'
      $temp =~ s/y'$/}/;              # y_w'_}
      push (@alternatives, $temp);    # y_w'_}   -- pushed
      if ($temp =~ s/w'/&/) {         # y_&__}
         push (@alternatives, $temp); # y_&__}   -- pushed
      }
   }
   elsif ($temp =~ m/y'$/) {          # Y_w'_y'
      if ($temp =~ s/Y/y/g) {         # Y_w'_y'
         push (@alternatives, $temp); # y_w'_y'  -- pushed
      }
      if ($temp =~ s/w'/&/) {         # y_w'_y'
         push (@alternatives, $temp); # y_&__y'  -- pushed
      }
      $temp = $word;                  # Y_w'_y'
      $temp =~ s/Y/y/g;               # y_w'_y'
      $temp =~ s/y'$/}/;              # y_w'_}
      push (@alternatives, $temp);    # y_w'_}   -- pushed
      if ($temp =~ s/w'/&/) {         # y_&__}
         push (@alternatives, $temp); # y_&__}   -- pushed
      }
   }
   elsif ($temp =~ s/Y$/y/) {         # Y_w'_y
      $temp =~ s/Y/y/g;               # y_w'_y
      push (@alternatives, $temp);    # y_w'_y   -- pushed
      if ($temp =~ s/w'/&/) {         # y_&__y
         push (@alternatives, $temp); # y_&__y   -- pushed
      }
   }
   elsif ($temp =~ m/y$/) {           # Y_w'_y
      $temp =~ s/Y/y/g;               # y_w'_y
      if ($temp =~ s/w'/&/) {         # y_&__y
         push (@alternatives, $temp); # y_&__y   -- pushed
      }
      $temp = $word;                  # Y_w'_y
      $temp =~ s/Y/y/g;               # y_w'_y
      $temp =~ s/y$/Y/g;              # y_w'_Y
      push (@alternatives, $temp);    # y_w'_Y   -- pushed
      if ($temp =~ s/w'/&/) {         # y_&__Y
         push (@alternatives, $temp); # y_&__Y   -- pushed
      }
   }
   elsif ($temp =~ m/h$/) {           # Y_w'_h
      if ($temp =~ s/Y/y/g) {         # y_w'_h
         push (@alternatives, $temp); # y_w'_h   -- pushed
      }
      if ($temp =~ s/w'/&/) {         # y_&__h
         push (@alternatives, $temp); # y_&__h   -- pushed
      }
      $temp =~ s/h$/p/;               # y_w'_p
      push (@alternatives, $temp);    # y_&__p   -- pushed
   }
   elsif ($temp =~ m/p$/) {           # Y_w'_h
      if ($temp =~ s/Y/y/g) {         # y_w'_h
         push (@alternatives, $temp); # y_w'_h   -- pushed
      }
      if ($temp =~ s/w'/&/) {         # y_&__h
         push (@alternatives, $temp); # y_&__h   -- pushed
      }
      $temp =~ s/p$/h/;               # y_w'_p
      push (@alternatives, $temp);    # y_&__p   -- pushed
   }
   elsif ($temp =~ s/Y/y/g) {         # Y_w'__
      push (@alternatives, $temp);    # y_w'__   -- pushed
      if ($temp =~ s/w'/&/) {         # y_&___
         push (@alternatives, $temp); # y_&___   -- pushed
      }
   }
   elsif ($temp =~ s/w'/&/) {         # y_w'__
         push (@alternatives, $temp); # y_&___   -- pushed
   }
   else {
      # nothing
   }

   return @alternatives;

}

# ============================
sub tokenize_nonArabic { # tokenize non-Arabic strings by splitting them on white space

   $nonArabic = shift @_;
   $nonArabic =~ s/^\s+//; $nonArabic =~ s/\s+$//; # remove leading & trailing space
   @nonArabictokens = split (/\s+/, $nonArabic);
   return @nonArabictokens;

}

# ============================
sub tokenize { # returns a list of tokens

   $line = shift @_;
   chomp($line);
   $line =~ s/^\s+//; $line =~ s/\s+$//; $line =~ s/\s+/ /g; # remove or minimize white space
   @tokens = split (/([^\x81\x8D\x8E\x90\xC1-\xD6\xD8-\xDF\xE1\xE3-\xE6\xEC-\xED\xF0-\xF3\xF5\xF6\xF8\xFA]+)/,$line);
   return @tokens;

}

# ================================
sub get_lookup { # creates a suitable lookup version of the Arabic input string (removes diacritics; transliterates)

   $input_str = shift @_;
   $tmp_word = $input_str; # we need to modify the input string for lookup
   $tmp_word =~ s/\xDC//g;  # remove kashida/taTwiyl (U+0640)
   $tmp_word =~ s/[\xF0-\xF3\xF5\xF6\xF8\xFA]//g;  # remove fatHatAn and all vowels/diacritics (ÒÚÛıˆ¯˙)
   $tmp_word =~ tr/\x81\x8D\x8E\x90\xA1\xBA\xBF\xC1\xC2\xC3\xC4\xC5\xC6\xC7\xC8\xC9\xCA\xCB\xCC\xCD\xCE\xCF\xD0\xD1\xD2\xD3\xD4\xD5\xD6\xD8\xD9\xDA\xDB\xDC\xDD\xDE\xDF\xE1\xE3\xE4\xE5\xE6\xEC\xED\xF0\xF1\xF2\xF3\xF5\xF6\xF8\xFA/PJRG,;?'|>&<}AbptvjHxd*rzs\$SDTZEg_fqklmnhwYyFNKaui~o/; # convert to transliteration
   return $tmp_word;

}

# ============================
sub segmentword { # returns a list of valid segmentations

   $str = shift @_;
   @segmented = ();
   $prefix_len = 0;
   $suffix_len = 0;
   $str_len = length($str);

   while ( $prefix_len <= 4 ) {
      $prefix = substr($str, 0, $prefix_len);
      $stem_len = ($str_len - $prefix_len); 
      $suffix_len = 0;
      while (($stem_len >= 1) and ($suffix_len <= 6)) {
         $stem   = substr($str, $prefix_len, $stem_len);
         $suffix = substr($str, ($prefix_len + $stem_len), $suffix_len);
         push (@segmented, "$prefix\t$stem\t$suffix");
         $stem_len--;
         $suffix_len++;
      }
      $prefix_len++;
   }
   return @segmented;

}

# ==============================================================
sub load_dict { # loads a dict into a hash table where the key is $entry and its value is a list (each $entry can have multiple values)

   %temp_hash = (); $entries = 0; $lemmaID = "";
   $filename = shift @_;
   open (IN, $filename) || die "cannot open: $!";
   print STDERR "loading $filename ...";
   while (<IN>) {
      if (m/^;; /) {  
         $lemmaID = $'; 
         chomp($lemmaID);
         if ( exists($seen{$lemmaID}) ) { 
            die "lemmaID $lemmaID in $filename (line $.) isn't unique\n" ; # lemmaID's must be unique
         }
         else { 
            $seen{$lemmaID} = 1; $lemmas++;
         } 
      } 
      elsif (m/^;/) {  } # comment
      else {
         chomp(); $entries++;
         # a little error-checking won't hurt:
         $trcnt = tr/\t/\t/; if ($trcnt != 3) { die "entry in $filename (line $.) doesn't have 4 fields (3 tabs)\n" };
         ($entry, $voc, $cat, $glossPOS) = split (/\t/, $_); # get the $entry for use as key
         # two ways to get the POS info:
         # (1) explicitly, by extracting it from the gloss field:
         if ($glossPOS =~ m!<pos>(.+?)</pos>!) {
            $POS = $1; # extract $POS from $glossPOS
            $gloss = $glossPOS; # we clean up the $gloss later (see below)
         }
         # (2) by deduction: use the $cat (and sometimes the $voc and $gloss) to deduce the appropriate POS
         else {
            $gloss = $glossPOS; # we need the $gloss to guess proper names
            if     ($cat  =~ m/^(Pref-0|Suff-0)$/)          {$POS = ""} # null prefix or suffix
            elsif  ($cat  =~ m/^F/)          {$POS = "$voc/FUNC_WORD"}
            elsif  ($cat  =~ m/^IV/)         {$POS = "$voc/VERB_IMPERFECT"}
            elsif  ($cat  =~ m/^PV/)         {$POS = "$voc/VERB_PERFECT"}
            elsif  ($cat  =~ m/^CV/)         {$POS = "$voc/VERB_IMPERATIVE"}
            elsif (($cat  =~ m/^N/)
              and ($gloss =~ m/^[A-Z]/))     {$POS = "$voc/NOUN_PROP"} # educated guess (99% correct)
            elsif (($cat  =~ m/^N/)
              and  ($voc  =~ m/iy~$/))       {$POS = "$voc/NOUN"} # (was NOUN_ADJ: some of these are really ADJ's and need to be tagged manually)
            elsif  ($cat  =~ m/^N/)          {$POS = "$voc/NOUN"}
            else                             { die "no POS can be deduced in $filename (line $.) "; }; 
         }

         # clean up the gloss: remove POS info and extra space, and convert upper-ASCII  to lower (it doesn't convert well to UTF-8)
         $gloss =~ s!<pos>.+?</pos>!!; $gloss =~ s/\s+$//; $gloss =~ s!;!/!g;
         $gloss =~ tr/¿¡¬√ƒ≈«»… ÀÃÕŒœ—“”‘’÷Ÿ⁄€‹/AAAAAACEEEEIIIINOOOOOUUUU/;
         $gloss =~ tr/‡·‚„‰ÂÁËÈÍÎÏÌÓÔÒÚÛÙıˆ˘˙˚¸/aaaaaaceeeeiiiinooooouuuu/;
         $gloss =~ s/∆/AE/g; $gloss =~ s/ä/Sh/g; $gloss =~ s/é/Zh/g; $gloss =~ s/ﬂ/ss/g;
         $gloss =~ s/Ê/ae/g; $gloss =~ s/ö/sh/g; $gloss =~ s/û/zh/g;

         # note that although we read 4 fields from the dict we now save 5 fields in the hash table
         # because the info in last field, $glossPOS, was split into two: $gloss and $POS
         #push ( @{ $temp_hash{$entry} }, "$entry\t$voc\t$cat\t$gloss\t$POS") ; # the value of $temp_hash{$entry} is a list of values
         push ( @{ $temp_hash{$entry} }, "$entry\t$voc\t$cat\t$gloss\t$POS\t$lemmaID") ; # the value of $temp_hash{$entry} is a list of values
      }
   }
   close IN;
   print STDERR "  $lemmas lemmas and" unless ($lemmaID eq "");
   print STDERR " $entries entries \n";
   return %temp_hash;

}

# ==============================================================
sub load_table { # loads a compatibility table into a hash table where the key is $_ and its value is 1

   %temp_hash = ();
   $filename = shift @_;
   open (IN, $filename) || die "cannot open: $!";
   while (<IN>) {
      unless ( m/^;/ ) {
         chomp();
         s/^\s+//; s/\s+$//; s/\s+/ /g; # remove or minimize white space
         $temp_hash{$_} = 1;
      }
   }
   close IN;
   return %temp_hash;

}
# ==============================================================

