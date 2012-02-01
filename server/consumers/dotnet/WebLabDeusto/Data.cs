namespace WebLabDeusto
{
    public class SessionId
    {
        private readonly string id;

        public SessionId(string id)
        {
            this.id = id;
        }

        public string Id
        {
            get{
                return this.id;
            }
        }

        public override string ToString()
        {
            return "SessionId(" + this.id + ")";
        }
    }

    public class ExperimentPermission
    {
        private readonly string name;
        private readonly string category;
        private readonly double assignedTime;

        public ExperimentPermission(string name, string category, double assignedTime)
        {
            this.name = name;
            this.category = category;
            this.assignedTime = assignedTime;
        }

        public string Name
        {
            get{
                return this.name;
            }
        }

        public string Category
        {
            get{
                return this.category;
            }
        }

        public double AssignedTime
        {
            get{
                return this.assignedTime;
            }
        }
    }

    public class ReservationId
    {
        private readonly string id;

        public ReservationId(string id)
        {
            this.id = id;
        }

        public string Id
        {
            get{
                return this.id;
            }
        }

        public override string ToString()
        {
            return "ReservationId(" + this.id + ")";
        }
    }

    public abstract class Reservation
    {
        protected readonly ReservationId reservationId;

        public Reservation(string reservationId)
        {
            this.reservationId = new ReservationId(reservationId);
        }

        public ReservationId ReservationId
        {
            get{
                return this.reservationId;
            }
        }
    }

    public class WaitingConfirmationReservation : Reservation
    {
        public WaitingConfirmationReservation(string reservationId):base(reservationId)
        { }

        public override string ToString()
        {
            return "WaitingConfirmationReservation(" + this.reservationId + ")";
        }
    }

    public class WaitingReservation : Reservation
    {
        private readonly int position;

        public WaitingReservation(string reservationId, int position):base(reservationId)
        {
            this.position = position;
        }

        public int Position
        {
            get{
                return this.position;
            }
        }

        public override string ToString() 
        {
            return "WaitingReservation(" + this.reservationId + ", " + this.position + ")";
        }
    }

    public class WaitingInstancesReservation : Reservation
    {
        private readonly int position;

        public WaitingInstancesReservation(string reservationId, int position) : base(reservationId)
        {
            this.position = position;
        }

        public int Position
        {
            get{
                return this.position;
            }
        }

        public override string ToString()
        {
            return "WaitingInstancesReservation(" + this.reservationId + ", " + this.position + ")";
        }
    }

    public class ConfirmedReservation : Reservation
    {
        private readonly double time;
        private readonly string initialConfiguration;
        private readonly string url;
        private readonly string remoteReservationId;

        public ConfirmedReservation(string reservationId, double time, string initialConfiguration, string url, string remoteReservationId) : base(reservationId)
        {
            this.time                 = time;
            this.initialConfiguration = initialConfiguration;
            this.url                  = url;
            this.remoteReservationId  = remoteReservationId;
        }

        public double Time
        {
            get{
                return this.time;
            }
        }

        public string InitialConfiguration
        {
            get{
                return this.initialConfiguration;
            }
        }

        public string Url
        {
            get{
                return this.url;
            }
        }

        public string RemoteReservationId
        {
            get{
                return this.remoteReservationId;
            }
        }

        public bool IsRemote
        {
            get{
                return this.remoteReservationId == null || this.remoteReservationId == "";
            }
        }

        public bool IsLocal
        {
            get{
                return !IsRemote;
            }
        }

        public override string ToString()
        {
            return "ConfirmedReservation(" + this.reservationId + ", " + this.time + ", " + this.initialConfiguration + ", " + this.url + ", " + this.remoteReservationId + ")";
        }
    }

    public class PostReservationReservation : Reservation
    {
        private readonly bool finished;
        private readonly string initialData;
        private readonly string endData;

        public PostReservationReservation(string reservationId, bool finished, string initialData, string endData) : base(reservationId)
        {
            this.finished    = finished;
            this.initialData = initialData;
            this.endData     = endData;
        }
        
        public bool IsFinished
        {
            get{
                return this.finished;
            }
        }

        public string InitialData
        {
            get{
                return this.initialData;
            }
        }

        public string EndData
        {
            get{
                return this.endData;
            }
        }

        public override string ToString()
        {
            return "PostReservationReservation( " + this.reservationId + ", " + this.finished + ", " + this.initialData + ", " + this.endData + ")";
        }
    }
}

