#--------------------------------------------------------------------------------------
class Out() :

  def open(self) :
    pass
  def close(self) :
    pass
  def image(self,img,title) :
    pass
  def h1(self,h1) :
    pass

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
    h2:before {
        content: counter(h2counter) ".  "; 
        counter-increment: h2counter;
        counter-reset: h3counter;
    }
    h3:before {
        content: counter(h2counter) "." counter(h3counter) ".  ";
        counter-increment: h3counter;
    }
    h2   {
          color: black;
          background-color: lightgrey;
          text-decoration: underline overline;
    }
    p    {color: black;}
    table, th, td {
      border-collapse: collapse;
      border: 1px solid black;
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

  def out(self,title,o) :
    print("<h3>"+title+"</h2>")
    if o.empty :
      return 
    print(o.to_html(border=1))

  def image(self,img,title) :
    print("<h3>" + title + "</h3>")
    print("<img src=\"" +img+ "\">")

#--------------------------------------------------------------------------------------
class OutputTty(Out) :

  def h1(self,h1) :
    print(h1)

  def out(self,title,o) :
    print("----------------------------------------------------------------")
    print(title)
    print(o)

