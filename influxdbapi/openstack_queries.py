from .base_queries import BaseQueries


class OpenStackQueries(BaseQueries):

    def mean_cpu_util(self, vdu_uuid):
        """ Get the mean cpu utilization (%)

        Args:
            vdu_uuid (str): the VDU uuid

        Returns:
            float: the mean cpu utilization (%)
        """
        return self.get_mean_metric(vdu_uuid, 'cpu_util')

    def mean_memory_util(self, vdu_uuid):
        """ Get the mean memory utilization (%)

        Args:
            vdu_uuid (str): the VDU uuid

        Returns:
            float: the mean memory utilization (%)
        """
        value = self.get_mean_metric(vdu_uuid, 'memory_util')
        if value is not None:
            value = value * 100
        return value

    def mean_disk_usage(self, vdu_uuid):
        """ Get the mean disk usage (bytes)

        Args:
            openstack_vim (str): The identifier of OpenStack VIM in OSM
            vdu_uuid (str): the VDU uuid
            time_range (int): the time range for the query

        Returns:
            float: the mean disk usage (bytes)
        """
        return self.get_mean_metric(vdu_uuid, 'disk.usage')

    def mean_disk_allocation(self, vdu_uuid):
        """ This query will fetch the mean value of the disk allocation in a
        VM hosted in the given OpenStack VIM (bytes)

        Args:
            vdu_uuid (str): the VDU uuid

        Returns:
            float:  the mean disk allocation (bytes)
        """
        return self.get_mean_metric(vdu_uuid, 'disk.allocation')

    def mean_disk_util(self, disk_usage, disk_allocation):
        """ This query calculate the mean disk utilization by given the mean
        disk usage and disk allocation.

        Args:
            disk_usage (float): The identifier of OpenStack VIM in OSM
            disk_allocation (float): the VDU uuid

        Returns:
            float:  the mean disk utilization (%)
        """
        mean_disk_util = None
        try:
            if disk_usage is not None and disk_allocation is not None and disk_allocation > 0:
                mean_disk_util = (disk_usage / disk_allocation) * 100.0
        except Exception as ex:
            pass
        finally:
            return mean_disk_util
