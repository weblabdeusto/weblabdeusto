<?php

/*********************************
* system.describeMethods Support *
*********************************/

/* public function. format method description. 
 * input = result from xmlrpc method "system.describeMethods" in a php array 
 * result = html string suitable for display.
 */
function format_describe_methods_result($response) {
   global $xi_type_hash;
   $unknown = "???";
   $method_hash = array();
   $xi_type_hash = array();

   $typeList = $response[typeList];
   $methodList = $response[methodList];

   usort(&$typeList, "name_cmp");
   usort(&$methodList, "name_cmp");

   if ($methodList) {
      $buf .= "<big>Methods\n<ul>";
      foreach($methodList as $method) {
         $name = $method[name];
         $buf .= "<li><a href='#$name'>$name()</a>\n";
         $method_hash[$name] = $method;
      }
      $buf .= "</ul></big>";
   }
   if ($typeList) {
      $buf .= "<big>Types\n<ul>";
      foreach($typeList as $type) {
         $name = $type[name];
         $buf .= "<li><a href='#$name'>$name</a>\n";
         $xi_type_hash[$name] = $type;
      }
      $buf .= "</ul></big>";
   }


   $buf .= "<h2>Methods</h2><table bgcolor='#dddddd' align='center' border=1 width=100%>";
   foreach($methodList as $method) {
      $name = $method[name];
      $author = $method[author] ? $method[author] : $unknown;
      $version = $method[version] ? $method[version] : $unknown;
      $desc = $method[purpose] ? $method[purpose] : $unknown;
      $sigs = $method[signatures];
      $buf .= "<tr bgcolor='#444444'><td align='center' class='title' colspan=3><font color='#EEEEEE'><a name='$name'><b><big>$name</big></b></a></font></td></tr>";
      $buf .= "<tr>" . field("Signature(s)", get_sigs($method), 3) . "</tr>";
      $buf .= "<tr>" . field("Author", $author, 2) . field("Version", $version) . "</tr>";
      $buf .= "<tr>" . field("Purpose", $desc, 3) . "</tr>";

      $exclude_list = array(
                           "see",
                           "signatures",
                           "purpose",
                           "version",
                           "author",
                           "name"
                           );
      foreach($method as $key => $val) {
         if (!in_array($key, $exclude_list)) {
            if (is_array($val)) {
               $buf .= "<tr bgcolor='#aaaaaa'><td colspan=3>" . ucfirst($key) . "</td></tr>";

               foreach($val as $key2 => $desc) {
                  if (gettype($desc) === "string") {
                     if (gettype($key2) !== "string") {
                        $key2 = false;
                     }

                     $buf .= "<tr>" . field(ucfirst($key2), $desc, 3) . "</tr>";
                  }
               }
            }
            else {
               $buf .= "<tr>" . field(ucfirst($key), $val, 3) . "</tr>";
            }
         }
      }


      if ($sigs) {
         $bmultiple = count($sigs) > 1;
         foreach($sigs as $sig) {
            if ($bmultiple) {
               $count ++;
               $buf .= "<tr bgcolor='#888888'><td colspan=3><font color='white'><b>Signature $count:</b> " . get_sig($name, $sig) . "</font></td></tr>";
            }

            if ($sig[params]) {
               $buf .= "<tr bgcolor='#aaaaaa'><td colspan=3>Parameters</td></tr>";

               $buf .= "<tr><td colspan=3>";
               $buf .= do_params($sig[params], false, false);
               $buf .= "</td></tr>";
            }

            if ($sig[returns]) {
               $buf .= "<tr bgcolor='#aaaaaa'><td colspan=3>Return Value(s)</td></tr>";
               $buf .= "<tr><td colspan=3>";
               $buf .= do_params($sig[returns], false, false);
               $buf .= "</td></tr>";
            }
         }
      }

      if ($method[see]) {
         $buf .= "<tr bgcolor='#aaaaaa'><td colspan=3>See Also</td></tr>";

         foreach($method[see] as $name => $desc) {
            if ($method_hash[$name]) {
               $name = "<a href='#$name'>$name</a>";
            }

            $buf .= "<tr>" . field($name, $desc, 3) . "</tr>";
         }
      }
   }
   $buf .= "</table><H2>Types</H2><TABLE><table bgcolor='#dddddd' align='center' border=1 width=100%>";
   $buf .= "<tr><td colspan=3>";

   $buf .= do_params($typeList, true);

   $buf .= "</td></tr>";
   $buf .= "</TABLE>";

   return $buf;
}

/*********************************************************************
* The following functions are non-public and may change at any time. *
*********************************************************************/

/* non public - format key/val pair in a <td></td> */
function field($title, $text, $columns=false, $width=false) {
   if ($columns) {
      $colspan = " colspan='$columns'";
   }
   if ($width) {
      $width = " width='$width' ";
   }
   $colon = $title && $text ? ":" : "";
   return "<td$colspan$width><b>$title$colon</b> $text</td>";
}

function is_xmlrpc_type($type) {
   static $types = array("array", "struct", "mixed", "string", "int", "i4", "datetime", "base64", "boolean");
   return in_array($type, $types);
}

function user_type($type) {
   global $xi_type_hash;
   return $xi_type_hash[$type] ? true : false;
}


function do_param($param, $bNewType=false, $bLinkUserTypes=true, $depth=0) {
   /* guard against serious craziness */
   if (++ $depth >= 24) {
      return "<dt><b>max depth reached.  bailing out...</b></dt>";
   }
   $name = $param[name];
   $type = $param[type];
   $desc = $param[description];
   $member = $param[member];
   $opt = $param[optional];
   $def = $param['default'];
   $type_def = $param[type_def];

   if ($type_def) {
      $type_def = "<a href='#$type_def'>$type_def</a> ";
   }
   else {
      $type_def = "";
   }

   $buf = "<dt>";

   if ($bNewType) {
      $anchor = "<a name='$name'></a>";
   }

   if (user_type($type)) {
      if ($bLinkUserTypes) {
         $type = "<a href='#$type'>$type</a>";
      }
      else {  
         /* hack to display user values inline.  max depth check above. */
         global $xi_type_hash;
         $newtype = $xi_type_hash[$type];

         $newtype[name] = $param[name];
         $newtype[optional] = $param[optional];
         if ($param[description]) {
            $newtype[description] = $param[description];
         }
         $newtype[type_def] = $type;
         $buf .= do_param($newtype, $bNewType, $bLinkUserTypes, $depth);
         return $buf;
      }
   }

   $buf .= "$type_def$type <i>$anchor$name</i>";
   if ($opt || $def) {
      $buf .= " (";
      if ($opt) {
         $buf .= "optional" . ($def ? ", " : "");
      }
      if ($def) {
         $buf .= "default=$def";
      }
      $buf .= ")";
   }

   if ($desc) {
      $buf .= " -- $desc";
   }
   if ($member) {
      $buf .= do_params($member, $bNewType, $bLinkUserTypes, $depth);
   }
   $buf .= "</dt>\n";

   return $buf;
}

/* non public - format params list recursively */
function do_params($params, $bNewType=false, $bLinkUserTypes=true, $depth=0) {
   if ($params) {
      $br = $bNewType ? "<br>" : "";
      $buf = "\n<dl>\n";
      foreach($params as $param) {
         $buf .= do_param($param, $bNewType, $bLinkUserTypes, $depth);
      }
      $buf .= "</dl>$br\n";
   }
   return $buf;
}


function get_sig($method_name, $sig) {
   $buf = "";
   if ($method_name && $sig) {
      $return = $sig[returns][0][type];
      if (!$return) {
         $return = "void";
      }
      $buf .= "$return ";

      $buf .= "$method_name( ";
      $first = true;

      if ($sig[params]) {
         foreach($sig[params] as $param) {
            $type = $param[type];
            $opt = $param[optional];
            $def = $param["default"];
            $name = $param["name"];
            if (user_type($type)) {
               $type = "<a href='#$type'>$type</a>";
            }

            if ($opt) {
               $buf .= $first ? '[' : ' [';
            }
            if (!$first) {
               $buf .= ', ';
            }
            $buf .= "$type";
            if (name) {
               $buf .= " $name";
            }
            if ($def) {
               $buf .= " = $def";
            }
            if ($opt) {
               $buf .= ']';
            }
            $first = false;
         }
      }

      $buf .= " )";
   }

   return $buf;
}

/* non public. generate method signature from method description */
function get_sigs($method) {
   $method_name = $method[name];

   $buf = "";

   if ($method[signatures]) {
      foreach($method[signatures] as $sig) {
         $buf .= "<li>" . get_sig($method_name, $sig);
      }
   }

   return $buf;
}

function name_cmp($a, $b) {
   return strcmp($a[name], $b[name]);
}


/*************************************
* END system.describeMethods Support *
*************************************/


?>
