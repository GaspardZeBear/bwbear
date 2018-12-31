#--------------------------------------------------------------------------------------
class Out() :

  def open(self) :
    pass
  def close(self) :
    pass
  def image(self,img,title) :
    print("<IMG> " + img)
  def h1(self,h1) :
    print("<H1> " + h1)
  def h2(self,h2) :
    print(" <H2> " + h2)

#--------------------------------------------------------------------------------------
class OutputHtml(Out) :

  #--------------------------------------------------------------------------------------
  def __init__(self) :
    self.tableOfContent=[]
    self.content=[]

  #--------------------------------------------------------------------------------------
  def addToContent(self,txt) :
    self.content.append(txt)

  #--------------------------------------------------------------------------------------
  def open(self) :
    head= """
    <html>
    <head>
    <style>
    body {
          background-color: white;
          counter-reset: h2counter;
          counter-reset: toc2counter;
    }
    h1   {
          color: black;
          background-color: grey;
          text-decoration: underline overline;
          counter-reset: h2counter;
    }
    h2:before {
        content: "Section " counter(h2counter) ".  "; 
        counter-increment: h2counter;
    }
    h2   {
          color: black;
          background-color: lightgrey;
          text-decoration: underline overline;
          counter-reset: h3counter;
    }
    h3:before {
        content: counter(h2counter) "." counter(h3counter) ".  ";
    }
    h3   {
          color: black;
          counter-increment: h3counter;
          text-decoration: underline;
    }

    p    {color: black;}
    table, th, td {
      border-collapse: collapse;
      border: 1px solid black;
      text-align: right;
    }
    div#tableOfContent {
	top: 50px;
	left: 0px;
	background-color:lightgrey;
    }
    div#content {
 	position:static;
    }
    div.toc2:before {
        content: "Section " counter(toc2counter) ".  "; 
        counter-increment: toc2counter;
    }
    div.toc2 {
 	color: black;
        font-weight:bold;
        counter-reset: toc3counter;
    }
    div.toc3:before {
        content: counter(toc2counter) "." counter(toc3counter) ".  ";
    }
    div.toc3 {
 	color: black;
        counter-increment: toc3counter;
    }
    ul {
        list-style-type: none;
    }
    </style>
    </head>
    <body>
    <a id="top"></a>
    """

    self.head=head

  #--------------------------------------------------------------------------------------
  def close(self) :
    print(self.head)
    print("<body>")
    print(self.h1)
    print("<div id=\"tableOfContent\">")
    #print("<ul>")
    for c in self.tableOfContent :
      print( c )
      #print("<li>" + c + "</li>")
    #print("</ul>")
    print("</div>")
    print("<div id=\"content\">")
    for c in self.content :
      print(c)
    print("</div>")
    print("</body>")
    print("</html>")

  #--------------------------------------------------------------------------------------
  def addToTableOfContent(self,level,title) :
    clazz="toc"+str(level)
    lnk="<a href=\"#" + str(abs(hash(title))) + "\">"
    self.tableOfContent.append("<div class=\"" + clazz + "\">" + lnk + title +  "</a></div>")

  #--------------------------------------------------------------------------------------
  def h1(self,h1) :
    self.h1="<h1>"+h1+"</h1>"

  #--------------------------------------------------------------------------------------
  def getDivId(self,h,title) :
    return("<div id=\"" + str(abs(hash(title))) +"\"></div><" + h + ">" + "<a href=\"#top\">&nbsp;&uarr;&nbsp;</a>"+ title + "</" + h + ">")

  #--------------------------------------------------------------------------------------
  def XgetTocDiv(self,h,title) :
    return("<div class=\"toc" + str(h) +"\">" +  title + "</div>")

  #--------------------------------------------------------------------------------------
  def h2(self,h2) :
    self.addToContent(self.getDivId("h2",h2))
    self.addToTableOfContent(2,h2)

  #--------------------------------------------------------------------------------------
  def h3(self,h3) :
    self.addToContent(self.getDivId("h3",h3))
    self.addToTableOfContent(3,h3)

  #--------------------------------------------------------------------------------------
  def p(self,p) :
    self.addToContent("<p>"+p+"</p>")

  #--------------------------------------------------------------------------------------
  def out(self,title,o) :
    self.addToContent("<br/><b>"+title+"</b>")
    if o.empty :
      return 
    self.addToContent(o.to_html(border=1))

  #--------------------------------------------------------------------------------------
  def tables(self,ths) :
    self.addToContent("<table>")
    self.addToContent("<tr>")
    for t in sorted(ths.keys()) :
      self.addToContent("<th>" + t + "</th>")
    self.addToContent("</tr>")
    self.addToContent("<tr>")
    for t in sorted(ths.keys()) :
      self.addToContent("<td>" + ths[t].to_html(border=1) + "</td>")
    self.addToContent("</tr>")
    self.addToContent("</table>")

  #--------------------------------------------------------------------------------------
  def image(self,img,title) :
    self.addToContent("<h4> Graph : " + title + "</h4>")
    self.addToContent("<img src=\"" +img+ "\">")

#--------------------------------------------------------------------------------------
class OutputTty(Out) :

  def h1(self,h1) :
    print(h1)

  def out(self,title,o) :
    print("----------------------------------------------------------------")
    print(title)
    print(o)

