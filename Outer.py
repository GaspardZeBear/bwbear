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

  def open(self) :
    print """
    <html>
    <head>
    <style>
    body {
          background-color: white;
          counter-reset: h2counter;
    }
    h1   {
          color: black;
          background-color: grey;
          text-decoration: underline overline;
          counter-reset: h2counter;
    }
    h2::before {
        content: "Section " counter(h2counter) ".  "; 
        counter-increment: h2counter;
    }
    h2   {
          color: black;
          background-color: lightgrey;
          text-decoration: underline overline;
          counter-reset: h3counter;
    }
    h3::before {
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
    </style>
    </head>
    <body>
    """

    print("<body>")

  def close(self) :
    print("</body>")
    print("</html>")

  def h1(self,h1) :
    print("<h1>"+h1+"</h1>")

  def h2(self,h2) :
    print("<h2>"+h2+"</h2>")

  def h3(self,h3) :
    print("<h3>"+h3+"</h3>")

  def p(self,p) :
    print("<p>"+p+"</p>")

  def out(self,title,o) :
    print("<h4>"+title+"</h4>")
    if o.empty :
      return 
    print(o.to_html(border=1))

  def image(self,img,title) :
    print("<h4> Graph : " + title + "</h4>")
    print("<img src=\"" +img+ "\">")

#--------------------------------------------------------------------------------------
class OutputTty(Out) :

  def h1(self,h1) :
    print(h1)

  def out(self,title,o) :
    print("----------------------------------------------------------------")
    print(title)
    print(o)

