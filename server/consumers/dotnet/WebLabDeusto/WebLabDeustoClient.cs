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

        public SessionId Login(string username, string password)
        {
            JsonData parameters = new JsonData();
            parameters["username"] = username;
            parameters["password"] = password;

            JsonData response = PerformRequest(LoginUrl, "login", parameters);

            return new SessionId((string)response["id"]);
        }

        public Reservation ReserveExperiment(SessionId sessid, string experimentName, string categoryName, string initialData)
        {
            JsonData parameters = new JsonData();
            parameters["session_id"] = new JsonData();
            parameters["session_id"]["id"] = sessid.Id;
            parameters["experiment_id"] = new JsonData();
            parameters["experiment_id"]["exp_name"] = experimentName;
            parameters["experiment_id"]["cat_name"] = categoryName;
            parameters["client_initial_data"] = initialData;
            parameters["consumer_data"] = "{}"; // TODO

            JsonData response = PerformCoreRequest("reserve_experiment", parameters);

            return parseReservation(response);
        }

        public Reservation GetReservationStatus(ReservationId reservationId)
        {
            JsonData parameters = new JsonData();
            parameters["reservation_id"] = new JsonData();
            parameters["reservation_id"]["id"] = reservationId.Id;

            JsonData response = PerformCoreRequest("get_reservation_status", parameters);

            return parseReservation(response);
        }

        public string CreateClient(Reservation reservation)
        {
            return this.url + "client/federated.html#reservation_id=" + reservation.ReservationId.Id;
        }

        private Reservation parseReservation(JsonData jsonReservation)
        {
            string reservationId = (string)jsonReservation["reservation_id"]["id"];
            string status = (string)jsonReservation["status"];
            switch(status)
            {
                case "Reservation::waiting_confirmation": 
                    return new WaitingConfirmationReservation(reservationId);

                case "Reservation::waiting":
                    return new WaitingReservation(reservationId, (int)jsonReservation["position"]);

                case "Reservation::waiting_instances":
                    return new WaitingInstancesReservation(reservationId, (int)jsonReservation["position"]);

                case "Reservation::confirmed":
                    return new ConfirmedReservation(reservationId, (double)jsonReservation["time"], (string)jsonReservation["initial_configuration"], (string)jsonReservation["url"], (string)jsonReservation["remote_reservation_id"]["id"]);

                case "Reservation::post_reservation":
                    return new PostReservationReservation(reservationId, (bool)jsonReservation["finished"], (string)jsonReservation["initial_data"], (string)jsonReservation["end_data"]);
            }
            throw new WebLabException("Could not parse reservation", ".NET WebLabDeusto");
        }

        private JsonData PerformCoreRequest(string method, JsonData parameters)
        {
            return PerformRequest(CoreUrl, method, parameters);
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

