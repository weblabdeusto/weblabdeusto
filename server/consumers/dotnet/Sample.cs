using System;
using WebLabDeusto;

namespace Sample
{

    public class WebLabDeustoSample 
    {
        public static void Main(string [] args)
        {
            WebLabDeustoClient weblab = new WebLabDeustoClient("http://localhost/weblab/");

            string sessionId = weblab.Login("any", "password");

            Console.WriteLine(sessionId);
        }
    }
}

