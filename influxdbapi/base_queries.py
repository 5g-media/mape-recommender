class BaseQueries:

    def __init__(self, client, vim_name, time_range=30):
        self.__client = client
        self.vim_name = vim_name
        self.time_range = time_range

    def get_vdu_list(self):
        """ Retrieve the list of VDU UUIDs from the InfluxDB by given the VIM name

        Returns:
            list: the VDUs list
        """
        query = "SHOW TAG VALUES FROM \"{}\"  WITH KEY =\"vdu_uuid\"".format(self.vim_name)
        rs = self.__client.query(query)
        records = list(rs.get_points(measurement=self.vim_name))
        vdus = [record['value'] for record in records]
        return vdus

    def get_vnfd_uuid(self, vdu_uuid):
        """ Retrieve the VNFd UUID from the InfluxDB by given the VDU UUID

        Returns:
            str: the VNFD UUID
        """
        query = "SHOW TAG VALUES FROM \"{}\"  WITH KEY =\"vnfd_id\" WHERE vdu_uuid=~/^{}$/".format(
            self.vim_name, vdu_uuid)
        result_set = self.__client.query(query)
        records = list(result_set.get_points(measurement=self.vim_name))
        if len(records):
            return records[0]['value']
        return None

    def get_vim_uuid(self, vdu_uuid):
        """ Retrieve the VIM UUID from the InfluxDB by given the VDU UUID

        Returns:
            str: the VIM UUID
        """
        query = "SHOW TAG VALUES FROM \"{}\"  WITH KEY =\"vim_uuid\" WHERE vdu_uuid=~/^{}$/".format(
            self.vim_name, vdu_uuid)
        result_set = self.__client.query(query)
        records = list(result_set.get_points(measurement=self.vim_name))
        if len(records):
            return records[0]['value']
        return None

    def get_mean_metric(self, vdu_uuid, metric):
        """ Calculate the mean value of a resource consumption metric in a given time range

        Args:
            vdu_uuid (str): The VDU identifier
            metric (str): The name of the resource consumption metric

        Returns:
            float: the mean value of the resource consumption metric
        """
        mean_metric = None
        try:
            query = "SELECT mean(\"value\") from /^{}$/ WHERE (\"vdu_uuid\"=~/^{}$/ and \"metric_name\"='{}') AND time >= now() - {}m".format(
                self.vim_name, vdu_uuid, metric, self.time_range)
            rs = self.__client.query(query)
            records = list(rs.get_points(measurement=self.vim_name))
            if len(records):
                mean_metric = records[0]['mean']
        except Exception as ex:
            pass
        finally:
            return mean_metric
