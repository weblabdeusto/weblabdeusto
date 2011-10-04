using System;
using System.Collections.Generic;
using System.IO;
using System.Net;
using System.Text;

using LitJson;

namespace WebLabDeusto
{
    public class WebLabDeustoClient
    {

        private readonly string url;
        private readonly CookieContainer cookieContainer = new CookieContainer();

        public WebLabDeustoClient(string url)
        {
            this.url = url;
        }

        public string LoginUrl{
            get{
                return this.url + "login/json/";
            }
        }

        public string CoreUrl{
            get{
                return this.url + "json/";
            }
        }

        public string Login(string username, string password)
        {
            JsonData parameters = new JsonData();
            parameters["username"] = username;
            parameters["password"] = password;

            JsonData response = PerformRequest(LoginUrl, "login", parameters);

            return (string)response["id"];
        }

        private JsonData PerformRequest(string url, string method, JsonData parameters)
        {
            JsonData request = new JsonData();
            request["method"] = method;
            request["params"] = parameters;

            string serializedResponse = PerformHttpRequest(url, request.ToJson());
            JsonData response = JsonMapper.ToObject( serializedResponse );
            
            if((bool)response["is_exception"])
                throw new WebLabException((string)response["message"], (string)response["code"]);
            else
                return response["result"];
        }

        private string PerformHttpRequest(string url, string payload)
        {
            UTF8Encoding encoding = new UTF8Encoding();
            byte[] byteData = encoding.GetBytes(payload);
            HttpWebRequest request = (HttpWebRequest)WebRequest.Create(url);
            request.Method = "POST";
            request.ContentType = "application/json";
            request.ContentLength = byteData.Length;
            request.CookieContainer = this.cookieContainer;

            Stream requestStream = request.GetRequestStream();
            requestStream.Write(byteData, 0, byteData.Length);
            requestStream.Close();

            HttpWebResponse response = (HttpWebResponse)request.GetResponse ();
            Stream dataStream = response.GetResponseStream ();
            StreamReader reader = new StreamReader (dataStream);
            return reader.ReadToEnd ();
        }
    }

    public class WebLabException : ApplicationException
    {
        private readonly string code;

        public WebLabException(string message, string code) : base(message)
        {
            this.code = code;
        }

        public string Code
        {
            get{
                return this.code;
            }
        }
    }
}

